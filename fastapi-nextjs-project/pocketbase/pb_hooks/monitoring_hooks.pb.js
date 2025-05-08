/// <reference path="../pb_data/types.d.ts" />

// Import required modules
const axios = require('axios');

// Define the backend API URL
const API_URL = 'http://localhost:8000/api/v1';

// Helper function to evaluate alert conditions
function evaluateCondition(condition, metricValue, thresholdValue) {
    // Convert values to numbers if possible
    let numericMetricValue = parseFloat(metricValue);
    let numericThresholdValue = parseFloat(thresholdValue);
    
    // If the values are not numeric, use string comparison
    if (isNaN(numericMetricValue) || isNaN(numericThresholdValue)) {
        // Special case for status
        if (condition === '=' || condition === '==') {
            return metricValue === thresholdValue;
        } else if (condition === '!=') {
            return metricValue !== thresholdValue;
        }
        return false;
    }
    
    // Numeric comparison
    switch (condition) {
        case '=':
        case '==':
            return numericMetricValue === numericThresholdValue;
        case '!=':
            return numericMetricValue !== numericThresholdValue;
        case '>':
            return numericMetricValue > numericThresholdValue;
        case '<':
            return numericMetricValue < numericThresholdValue;
        case '>=':
            return numericMetricValue >= numericThresholdValue;
        case '<=':
            return numericMetricValue <= numericThresholdValue;
        default:
            return false;
    }
}

// Hook: After a database is added, create initial status record
onModelAfterCreate((e) => {
    const collection = e.model.collection().name;
    
    if (collection !== 'monitored_databases') {
        return;
    }
    
    // Create initial status record
    const database = e.model;
    
    try {
        const statusRecord = $app.dao().findFirstRecordByData('database_status', {
            'database': database.id
        });
        
        if (!statusRecord) {
            $app.dao().saveRecord(new Record($app.dao().findCollectionByNameOrId('database_status'), {
                'database': database.id,
                'status': 'unknown',
                'last_check': new Date().toISOString()
            }));
        }
        
        // Schedule the first status check
        setTimeout(() => {
            checkDatabaseStatus(database.id);
        }, 5000); // Wait 5 seconds before first check
        
    } catch (err) {
        console.error('Error creating initial status record:', err);
    }
}, 'monitored_databases');

// Function to check database status
async function checkDatabaseStatus(databaseId) {
    try {
        // Get the database record
        const database = $app.dao().findRecordById('monitored_databases', databaseId);
        if (!database) {
            console.error(`Database with ID ${databaseId} not found`);
            return;
        }
        
        // Get database configuration
        const config = {
            instance_connection_name: database.get('instance_connection_name'),
            database: database.get('database'),
            user: database.get('user'),
            password: database.get('password'),
            ip_type: database.get('ip_type')
        };
        
        // Call the API to check database status
        const response = await axios.post(`${API_URL}/cloudsql/instances/status`, config);
        const statusData = response.data;
        
        // Update the status record
        let statusRecord = $app.dao().findFirstRecordByData('database_status', {
            'database': databaseId
        });
        
        if (!statusRecord) {
            statusRecord = new Record($app.dao().findCollectionByNameOrId('database_status'), {
                'database': databaseId
            });
        }
        
        // Update fields
        statusRecord.set('status', statusData.status);
        statusRecord.set('last_check', new Date().toISOString());
        
        if (statusData.status === 'online') {
            statusRecord.set('version', statusData.version || '');
            statusRecord.set('uptime', statusData.uptime || '');
            statusRecord.set('connection_count', statusData.connection_count || 0);
            statusRecord.set('size', statusData.size || '');
            statusRecord.set('table_count', statusData.table_count || 0);
            statusRecord.set('has_postgis', statusData.has_postgis || false);
            statusRecord.set('postgis_version', statusData.postgis_version || '');
            statusRecord.set('error_message', '');
        } else {
            statusRecord.set('error_message', statusData.error || 'Unknown error');
        }
        
        $app.dao().saveRecord(statusRecord);
        
        // Get performance metrics if database is online
        if (statusData.status === 'online') {
            try {
                const metricsResponse = await axios.post(`${API_URL}/cloudsql/instances/metrics`, config);
                const metricsData = metricsResponse.data;
                
                // Create a new performance metrics record
                const metricsRecord = new Record($app.dao().findCollectionByNameOrId('performance_metrics'), {
                    'database': databaseId,
                    'timestamp': new Date().toISOString(),
                    'cache_hit_ratio': metricsData.cache_hit_ratio || 0,
                    'metrics_json': JSON.stringify(metricsData)
                });
                
                // Extract key metrics
                if (metricsData.database_stats) {
                    metricsRecord.set('active_connections', metricsData.database_stats.connections || 0);
                    metricsRecord.set('transactions_per_second', metricsData.database_stats.commits || 0);
                    
                    // Calculate queries per second (approximate)
                    const qps = (metricsData.database_stats.rows_fetched || 0) / 60; // Assuming 1-minute interval
                    metricsRecord.set('queries_per_second', qps);
                    
                    // Calculate rows per second
                    const rps = (
                        (metricsData.database_stats.rows_returned || 0) +
                        (metricsData.database_stats.rows_fetched || 0)
                    ) / 60;
                    metricsRecord.set('rows_per_second', rps);
                    
                    // Set deadlocks
                    metricsRecord.set('deadlocks', metricsData.database_stats.deadlocks || 0);
                }
                
                // Count slow queries
                let slowQueries = 0;
                if (metricsData.query_stats) {
                    slowQueries = metricsData.query_stats.filter(q => q.duration_seconds > 1).length;
                }
                metricsRecord.set('slow_queries', slowQueries);
                
                $app.dao().saveRecord(metricsRecord);
                
                // Check for alerts
                checkAlerts(databaseId, statusData, metricsData);
                
            } catch (metricsErr) {
                console.error(`Error getting metrics for database ${databaseId}:`, metricsErr);
            }
        }
        
        // Schedule next check based on the interval
        const intervalMinutes = database.get('check_interval_minutes') || 5;
        setTimeout(() => {
            checkDatabaseStatus(databaseId);
        }, intervalMinutes * 60 * 1000);
        
    } catch (err) {
        console.error(`Error checking status for database ${databaseId}:`, err);
        
        // Update status to offline with error
        try {
            let statusRecord = $app.dao().findFirstRecordByData('database_status', {
                'database': databaseId
            });
            
            if (!statusRecord) {
                statusRecord = new Record($app.dao().findCollectionByNameOrId('database_status'), {
                    'database': databaseId
                });
            }
            
            statusRecord.set('status', 'offline');
            statusRecord.set('last_check', new Date().toISOString());
            statusRecord.set('error_message', err.message || 'Unknown error');
            
            $app.dao().saveRecord(statusRecord);
        } catch (updateErr) {
            console.error('Error updating status record:', updateErr);
        }
        
        // Schedule next check (use shorter interval for errors)
        setTimeout(() => {
            checkDatabaseStatus(databaseId);
        }, 2 * 60 * 1000); // 2 minutes
    }
}

// Function to check alerts
function checkAlerts(databaseId, statusData, metricsData) {
    try {
        // Get all alert rules for this database
        const rules = $app.dao().findRecordsByFilter(
            'alert_rules',
            `database = '${databaseId}' && enabled = true`
        );
        
        for (const rule of rules) {
            const metric = rule.get('metric');
            const condition = rule.get('condition');
            const thresholdValue = rule.get('value');
            const severity = rule.get('severity');
            
            let metricValue;
            let metricSource;
            
            // Get the metric value based on the metric type
            if (metric === 'status') {
                metricValue = statusData.status;
                metricSource = statusData;
            } else if (metric === 'connection_count') {
                metricValue = statusData.connection_count;
                metricSource = statusData;
            } else {
                // Performance metrics
                if (metric === 'cache_hit_ratio') {
                    metricValue = metricsData.cache_hit_ratio;
                } else if (metric === 'active_connections') {
                    metricValue = metricsData.database_stats?.connections;
                } else if (metric === 'transactions_per_second') {
                    metricValue = metricsData.database_stats?.commits;
                } else if (metric === 'queries_per_second') {
                    metricValue = (metricsData.database_stats?.rows_fetched || 0) / 60;
                } else if (metric === 'slow_queries') {
                    metricValue = metricsData.query_stats?.filter(q => q.duration_seconds > 1).length;
                } else if (metric === 'deadlocks') {
                    metricValue = metricsData.database_stats?.deadlocks;
                }
                metricSource = metricsData;
            }
            
            // Skip if metric value is undefined
            if (metricValue === undefined) {
                continue;
            }
            
            // Evaluate the condition
            const isAlertTriggered = evaluateCondition(condition, metricValue, thresholdValue);
            
            if (isAlertTriggered) {
                // Check if there's already an active alert for this rule
                const existingAlert = $app.dao().findFirstRecordByFilter(
                    'alerts',
                    `rule = '${rule.id}' && status != 'resolved'`
                );
                
                if (!existingAlert) {
                    // Create a new alert
                    const alertMessage = `Alert: ${rule.get('name')} - ${metric} ${condition} ${thresholdValue} (Current value: ${metricValue})`;
                    
                    const alertRecord = new Record($app.dao().findCollectionByNameOrId('alerts'), {
                        'rule': rule.id,
                        'database': databaseId,
                        'status': 'triggered',
                        'severity': severity,
                        'message': alertMessage,
                        'metric_value': String(metricValue),
                        'triggered_at': new Date().toISOString()
                    });
                    
                    $app.dao().saveRecord(alertRecord);
                    
                    // Send notifications
                    sendAlertNotifications(rule, alertRecord, metricValue);
                }
            } else {
                // Check if there are any active alerts for this rule that should be resolved
                const activeAlerts = $app.dao().findRecordsByFilter(
                    'alerts',
                    `rule = '${rule.id}' && status != 'resolved'`
                );
                
                for (const alert of activeAlerts) {
                    // Resolve the alert
                    alert.set('status', 'resolved');
                    alert.set('resolved_at', new Date().toISOString());
                    $app.dao().saveRecord(alert);
                }
            }
        }
    } catch (err) {
        console.error(`Error checking alerts for database ${databaseId}:`, err);
    }
}

// Function to send alert notifications
function sendAlertNotifications(rule, alert, metricValue) {
    const notificationChannels = rule.get('notification_channels') || [];
    
    // Send in-app notification (always happens)
    console.log(`Alert triggered: ${alert.get('message')}`);
    
    // Send email notification
    if (notificationChannels.includes('email')) {
        // Get the database owner
        const database = $app.dao().findRecordById('monitored_databases', alert.get('database'));
        if (database) {
            const owner = $app.dao().findRecordById('_pb_users_auth_', database.get('owner'));
            if (owner) {
                const email = owner.get('email');
                if (email) {
                    // Send email
                    $app.newMailClient().sendMail({
                        to: email,
                        subject: `Database Alert: ${rule.get('name')}`,
                        html: `
                            <h1>Database Alert</h1>
                            <p><strong>Alert:</strong> ${rule.get('name')}</p>
                            <p><strong>Database:</strong> ${database.get('name')}</p>
                            <p><strong>Severity:</strong> ${alert.get('severity')}</p>
                            <p><strong>Message:</strong> ${alert.get('message')}</p>
                            <p><strong>Triggered at:</strong> ${new Date(alert.get('triggered_at')).toLocaleString()}</p>
                            <p>Please check your database monitoring dashboard for more details.</p>
                        `
                    });
                }
            }
        }
    }
    
    // Send webhook notification
    if (notificationChannels.includes('webhook')) {
        const webhookUrl = rule.get('webhook_url');
        if (webhookUrl) {
            try {
                axios.post(webhookUrl, {
                    alert_id: alert.id,
                    rule_name: rule.get('name'),
                    database_id: alert.get('database'),
                    severity: alert.get('severity'),
                    message: alert.get('message'),
                    metric_value: metricValue,
                    triggered_at: alert.get('triggered_at')
                });
            } catch (err) {
                console.error('Error sending webhook notification:', err);
            }
        }
    }
}

// Hook: After a database is updated, update monitoring schedule
onModelAfterUpdate((e) => {
    const collection = e.model.collection().name;
    
    if (collection !== 'monitored_databases') {
        return;
    }
    
    // If check_interval_minutes changed, we'll let the next scheduled check handle it
    // No need to do anything special here
}, 'monitored_databases');

// Hook: After an alert is acknowledged
onModelAfterUpdate((e) => {
    const collection = e.model.collection().name;
    
    if (collection !== 'alerts') {
        return;
    }
    
    const alert = e.model;
    const oldStatus = e.model.originalModel().get('status');
    const newStatus = alert.get('status');
    
    // If status changed from triggered to acknowledged
    if (oldStatus === 'triggered' && newStatus === 'acknowledged') {
        // Update acknowledged_at timestamp
        alert.set('acknowledged_at', new Date().toISOString());
        $app.dao().saveRecord(alert);
    }
}, 'alerts');

// Initialize monitoring for all databases on server start
onServerStart(() => {
    setTimeout(() => {
        try {
            const databases = $app.dao().findRecordsByFilter('monitored_databases', '');
            
            for (const database of databases) {
                // Schedule status check with a random delay to avoid all checks happening at once
                const randomDelay = Math.floor(Math.random() * 30) * 1000; // 0-30 seconds
                setTimeout(() => {
                    checkDatabaseStatus(database.id);
                }, randomDelay);
            }
        } catch (err) {
            console.error('Error initializing database monitoring:', err);
        }
    }, 10000); // Wait 10 seconds after server start
});
