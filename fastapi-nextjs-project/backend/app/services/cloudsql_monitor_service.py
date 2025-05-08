import os
import time
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud.sql.connector.error import CloudSQLError

logger = logging.getLogger(__name__)

class CloudSQLMonitorService:
    """
    Service for monitoring Google Cloud SQL PostgreSQL instances
    """
    
    def __init__(self):
        """Initialize the Cloud SQL Monitor Service"""
        self.connector = Connector()
        self.connections = {}
        self.metrics_cache = {}
        self.metrics_cache_time = {}
        self.cache_ttl = 60  # Cache TTL in seconds
    
    async def get_connection(self, instance_config: Dict[str, Any]) -> psycopg2.connection:
        """
        Get a connection to a Cloud SQL instance
        
        Args:
            instance_config: Configuration for the instance
                {
                    "instance_connection_name": "project:region:instance",
                    "database": "database_name",
                    "user": "username",
                    "password": "password",
                    "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
                }
        
        Returns:
            Database connection
        """
        connection_key = f"{instance_config['instance_connection_name']}:{instance_config['database']}"
        
        # Check if connection exists and is valid
        if connection_key in self.connections:
            conn = self.connections[connection_key]
            try:
                # Check if connection is still valid
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return conn
            except (psycopg2.Error, Exception):
                # Connection is invalid, close it
                try:
                    conn.close()
                except:
                    pass
                del self.connections[connection_key]
        
        # Create new connection
        try:
            # Determine IP type
            ip_type = IPTypes.PUBLIC
            if instance_config.get("ip_type") == "PRIVATE":
                ip_type = IPTypes.PRIVATE
            
            # Create connection
            conn = await asyncio.to_thread(
                self.connector.connect,
                instance_config["instance_connection_name"],
                "pg8000",
                user=instance_config["user"],
                password=instance_config["password"],
                db=instance_config["database"],
                ip_type=ip_type
            )
            
            # Store connection
            self.connections[connection_key] = conn
            return conn
        except Exception as e:
            logger.error(f"Error connecting to Cloud SQL instance: {str(e)}")
            raise
    
    async def close_connections(self):
        """Close all connections"""
        for conn in self.connections.values():
            try:
                conn.close()
            except:
                pass
        self.connections = {}
    
    async def get_instance_status(self, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get status of a Cloud SQL instance
        
        Args:
            instance_config: Configuration for the instance
        
        Returns:
            Dictionary with instance status
        """
        try:
            # Get connection
            conn = await self.get_connection(instance_config)
            
            # Check connection
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get PostgreSQL version
                cursor.execute("SELECT version()")
                version = cursor.fetchone()["version"]
                
                # Get uptime
                cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime")
                uptime = cursor.fetchone()["uptime"]
                
                # Get connection count
                cursor.execute("SELECT count(*) as connection_count FROM pg_stat_activity")
                connection_count = cursor.fetchone()["connection_count"]
                
                # Get database size
                cursor.execute(f"SELECT pg_size_pretty(pg_database_size('{instance_config['database']}')) as size")
                db_size = cursor.fetchone()["size"]
                
                # Get table count
                cursor.execute("""
                    SELECT count(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                """)
                table_count = cursor.fetchone()["table_count"]
                
                # Check if PostGIS is installed
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_extension WHERE extname = 'postgis'
                    ) as has_postgis
                """)
                has_postgis = cursor.fetchone()["has_postgis"]
                
                # Get PostGIS version if installed
                postgis_version = None
                if has_postgis:
                    cursor.execute("SELECT PostGIS_Version() as version")
                    postgis_version = cursor.fetchone()["version"]
            
            # Return status
            return {
                "status": "online",
                "instance": instance_config["instance_connection_name"],
                "database": instance_config["database"],
                "version": version,
                "uptime": str(uptime),
                "connection_count": connection_count,
                "size": db_size,
                "table_count": table_count,
                "has_postgis": has_postgis,
                "postgis_version": postgis_version,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting instance status: {str(e)}")
            return {
                "status": "offline",
                "instance": instance_config["instance_connection_name"],
                "database": instance_config["database"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_performance_metrics(self, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get performance metrics for a Cloud SQL instance
        
        Args:
            instance_config: Configuration for the instance
        
        Returns:
            Dictionary with performance metrics
        """
        # Check cache
        cache_key = f"{instance_config['instance_connection_name']}:{instance_config['database']}"
        if cache_key in self.metrics_cache:
            cache_time = self.metrics_cache_time.get(cache_key)
            if cache_time and (datetime.now() - cache_time).total_seconds() < self.cache_ttl:
                return self.metrics_cache[cache_key]
        
        try:
            # Get connection
            conn = await self.get_connection(instance_config)
            
            # Get metrics
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get database statistics
                cursor.execute("""
                    SELECT 
                        datname as database_name,
                        numbackends as connections,
                        xact_commit as commits,
                        xact_rollback as rollbacks,
                        blks_read as blocks_read,
                        blks_hit as blocks_hit,
                        tup_returned as rows_returned,
                        tup_fetched as rows_fetched,
                        tup_inserted as rows_inserted,
                        tup_updated as rows_updated,
                        tup_deleted as rows_deleted,
                        conflicts,
                        temp_files,
                        temp_bytes,
                        deadlocks,
                        blk_read_time as read_time_ms,
                        blk_write_time as write_time_ms
                    FROM pg_stat_database
                    WHERE datname = %s
                """, (instance_config["database"],))
                db_stats = cursor.fetchone()
                
                # Get table statistics
                cursor.execute("""
                    SELECT 
                        schemaname as schema,
                        relname as table_name,
                        seq_scan,
                        seq_tup_read as sequential_rows_read,
                        idx_scan as index_scans,
                        idx_tup_fetch as index_rows_fetched,
                        n_tup_ins as rows_inserted,
                        n_tup_upd as rows_updated,
                        n_tup_del as rows_deleted,
                        n_live_tup as live_rows,
                        n_dead_tup as dead_rows,
                        vacuum_count,
                        autovacuum_count,
                        analyze_count,
                        autoanalyze_count
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                    LIMIT 10
                """)
                table_stats = cursor.fetchall()
                
                # Get index statistics
                cursor.execute("""
                    SELECT 
                        schemaname as schema,
                        relname as table_name,
                        indexrelname as index_name,
                        idx_scan as scans,
                        idx_tup_read as rows_read,
                        idx_tup_fetch as rows_fetched
                    FROM pg_stat_user_indexes
                    ORDER BY idx_scan DESC
                    LIMIT 10
                """)
                index_stats = cursor.fetchall()
                
                # Get query statistics
                cursor.execute("""
                    SELECT 
                        datname as database_name,
                        usename as username,
                        state,
                        query,
                        EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds
                    FROM pg_stat_activity
                    WHERE state != 'idle'
                    AND query != '<IDLE>'
                    AND query NOT ILIKE '%pg_stat_activity%'
                    ORDER BY duration_seconds DESC
                    LIMIT 10
                """)
                query_stats = cursor.fetchall()
                
                # Get lock statistics
                cursor.execute("""
                    SELECT 
                        locktype,
                        relation::regclass as table_name,
                        mode,
                        granted,
                        count(*) as lock_count
                    FROM pg_locks
                    GROUP BY locktype, relation, mode, granted
                    ORDER BY count(*) DESC
                    LIMIT 10
                """)
                lock_stats = cursor.fetchall()
                
                # Calculate cache hit ratio
                cache_hit_ratio = 0
                if db_stats["blocks_read"] + db_stats["blocks_hit"] > 0:
                    cache_hit_ratio = db_stats["blocks_hit"] / (db_stats["blocks_read"] + db_stats["blocks_hit"]) * 100
            
            # Prepare metrics
            metrics = {
                "instance": instance_config["instance_connection_name"],
                "database": instance_config["database"],
                "timestamp": datetime.now().isoformat(),
                "database_stats": dict(db_stats) if db_stats else {},
                "cache_hit_ratio": round(cache_hit_ratio, 2),
                "table_stats": [dict(stat) for stat in table_stats],
                "index_stats": [dict(stat) for stat in index_stats],
                "query_stats": [dict(stat) for stat in query_stats],
                "lock_stats": [dict(stat) for stat in lock_stats]
            }
            
            # Update cache
            self.metrics_cache[cache_key] = metrics
            self.metrics_cache_time[cache_key] = datetime.now()
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {
                "instance": instance_config["instance_connection_name"],
                "database": instance_config["database"],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def get_table_sizes(self, instance_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get table sizes for a Cloud SQL instance
        
        Args:
            instance_config: Configuration for the instance
        
        Returns:
            List of dictionaries with table sizes
        """
        try:
            # Get connection
            conn = await self.get_connection(instance_config)
            
            # Get table sizes
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        schemaname as schema,
                        relname as table_name,
                        pg_size_pretty(pg_total_relation_size(schemaname || '.' || relname)) as total_size,
                        pg_size_pretty(pg_relation_size(schemaname || '.' || relname)) as table_size,
                        pg_size_pretty(pg_total_relation_size(schemaname || '.' || relname) - 
                                      pg_relation_size(schemaname || '.' || relname)) as index_size,
                        pg_total_relation_size(schemaname || '.' || relname) as total_bytes
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname || '.' || relname) DESC
                    LIMIT 20
                """)
                table_sizes = cursor.fetchall()
            
            return [dict(size) for size in table_sizes]
        except Exception as e:
            logger.error(f"Error getting table sizes: {str(e)}")
            return []
    
    async def get_postgis_stats(self, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get PostGIS statistics for a Cloud SQL instance
        
        Args:
            instance_config: Configuration for the instance
        
        Returns:
            Dictionary with PostGIS statistics
        """
        try:
            # Get connection
            conn = await self.get_connection(instance_config)
            
            # Check if PostGIS is installed
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_extension WHERE extname = 'postgis'
                    ) as has_postgis
                """)
                has_postgis = cursor.fetchone()["has_postgis"]
                
                if not has_postgis:
                    return {
                        "has_postgis": False,
                        "instance": instance_config["instance_connection_name"],
                        "database": instance_config["database"]
                    }
                
                # Get PostGIS version
                cursor.execute("SELECT PostGIS_Version() as version")
                postgis_version = cursor.fetchone()["version"]
                
                # Get geometry column statistics
                cursor.execute("""
                    SELECT 
                        f_table_schema as schema,
                        f_table_name as table_name,
                        f_geometry_column as geometry_column,
                        type as geometry_type,
                        srid,
                        coord_dimension as dimensions
                    FROM geometry_columns
                    ORDER BY f_table_schema, f_table_name
                """)
                geometry_columns = cursor.fetchall()
                
                # Get spatial reference systems
                cursor.execute("""
                    SELECT 
                        srid,
                        auth_name,
                        auth_srid,
                        srtext
                    FROM spatial_ref_sys
                    WHERE srid IN (
                        SELECT DISTINCT srid FROM geometry_columns
                    )
                    ORDER BY srid
                """)
                spatial_ref_systems = cursor.fetchall()
                
                # Get geometry statistics for each table
                geometry_stats = []
                for col in geometry_columns:
                    try:
                        cursor.execute(f"""
                            SELECT 
                                COUNT(*) as feature_count,
                                ST_AsText(ST_Extent({col['geometry_column']})) as extent
                            FROM {col['schema']}.{col['table_name']}
                        """)
                        stats = cursor.fetchone()
                        
                        geometry_stats.append({
                            "schema": col["schema"],
                            "table_name": col["table_name"],
                            "geometry_column": col["geometry_column"],
                            "feature_count": stats["feature_count"],
                            "extent": stats["extent"]
                        })
                    except Exception as e:
                        logger.error(f"Error getting geometry statistics: {str(e)}")
                        geometry_stats.append({
                            "schema": col["schema"],
                            "table_name": col["table_name"],
                            "geometry_column": col["geometry_column"],
                            "error": str(e)
                        })
            
            return {
                "has_postgis": True,
                "instance": instance_config["instance_connection_name"],
                "database": instance_config["database"],
                "postgis_version": postgis_version,
                "geometry_columns": [dict(col) for col in geometry_columns],
                "spatial_ref_systems": [dict(srs) for srs in spatial_ref_systems],
                "geometry_stats": geometry_stats
            }
        except Exception as e:
            logger.error(f"Error getting PostGIS statistics: {str(e)}")
            return {
                "has_postgis": False,
                "instance": instance_config["instance_connection_name"],
                "database": instance_config["database"],
                "error": str(e)
            }
    
    async def run_custom_query(self, instance_config: Dict[str, Any], query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        Run a custom query on a Cloud SQL instance
        
        Args:
            instance_config: Configuration for the instance
            query: SQL query to run
            params: Query parameters
            
        Returns:
            List of dictionaries with query results
        """
        try:
            # Get connection
            conn = await self.get_connection(instance_config)
            
            # Run query
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or [])
                results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error running custom query: {str(e)}")
            raise
