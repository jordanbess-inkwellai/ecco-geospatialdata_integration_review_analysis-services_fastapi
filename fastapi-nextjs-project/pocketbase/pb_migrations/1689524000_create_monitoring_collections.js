/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  // Create monitored_databases collection
  const monitored_databases = new Collection({
    name: 'monitored_databases',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'name',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'instance_connection_name',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 200
        }
      },
      {
        name: 'database',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'user',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'password',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'ip_type',
        type: 'select',
        required: true,
        options: {
          values: ['PUBLIC', 'PRIVATE']
        }
      },
      {
        name: 'check_interval_minutes',
        type: 'number',
        required: true,
        options: {
          min: 1,
          max: 1440
        }
      },
      {
        name: 'owner',
        type: 'relation',
        required: true,
        options: {
          collectionId: '_pb_users_auth_',
          cascadeDelete: false
        }
      }
    ],
    indexes: [
      'CREATE UNIQUE INDEX idx_unique_instance_db ON monitored_databases (instance_connection_name, database)'
    ],
    listRule: '@request.auth.id = owner.id',
    viewRule: '@request.auth.id = owner.id',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = owner.id',
    deleteRule: '@request.auth.id = owner.id'
  });

  // Create database_status collection
  const database_status = new Collection({
    name: 'database_status',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'database',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'monitored_databases',
          cascadeDelete: true
        }
      },
      {
        name: 'status',
        type: 'select',
        required: true,
        options: {
          values: ['online', 'offline', 'degraded', 'unknown']
        }
      },
      {
        name: 'version',
        type: 'text',
        required: false
      },
      {
        name: 'uptime',
        type: 'text',
        required: false
      },
      {
        name: 'connection_count',
        type: 'number',
        required: false
      },
      {
        name: 'size',
        type: 'text',
        required: false
      },
      {
        name: 'table_count',
        type: 'number',
        required: false
      },
      {
        name: 'has_postgis',
        type: 'bool',
        required: false
      },
      {
        name: 'postgis_version',
        type: 'text',
        required: false
      },
      {
        name: 'error_message',
        type: 'text',
        required: false
      },
      {
        name: 'last_check',
        type: 'date',
        required: true,
        options: {
          min: '',
          max: ''
        }
      }
    ],
    indexes: [
      'CREATE INDEX idx_database_status_database ON database_status (database)'
    ],
    listRule: '@request.auth.id = database.owner.id',
    viewRule: '@request.auth.id = database.owner.id',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = database.owner.id',
    deleteRule: '@request.auth.id = database.owner.id'
  });

  // Create performance_metrics collection
  const performance_metrics = new Collection({
    name: 'performance_metrics',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'database',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'monitored_databases',
          cascadeDelete: true
        }
      },
      {
        name: 'cache_hit_ratio',
        type: 'number',
        required: false
      },
      {
        name: 'active_connections',
        type: 'number',
        required: false
      },
      {
        name: 'idle_connections',
        type: 'number',
        required: false
      },
      {
        name: 'transactions_per_second',
        type: 'number',
        required: false
      },
      {
        name: 'queries_per_second',
        type: 'number',
        required: false
      },
      {
        name: 'rows_per_second',
        type: 'number',
        required: false
      },
      {
        name: 'index_hit_ratio',
        type: 'number',
        required: false
      },
      {
        name: 'slow_queries',
        type: 'number',
        required: false
      },
      {
        name: 'deadlocks',
        type: 'number',
        required: false
      },
      {
        name: 'metrics_json',
        type: 'json',
        required: false
      },
      {
        name: 'timestamp',
        type: 'date',
        required: true,
        options: {
          min: '',
          max: ''
        }
      }
    ],
    indexes: [
      'CREATE INDEX idx_perf_metrics_database ON performance_metrics (database)',
      'CREATE INDEX idx_perf_metrics_timestamp ON performance_metrics (timestamp)'
    ],
    listRule: '@request.auth.id = database.owner.id',
    viewRule: '@request.auth.id = database.owner.id',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = database.owner.id',
    deleteRule: '@request.auth.id = database.owner.id'
  });

  // Create alert_rules collection
  const alert_rules = new Collection({
    name: 'alert_rules',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'name',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'database',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'monitored_databases',
          cascadeDelete: true
        }
      },
      {
        name: 'metric',
        type: 'select',
        required: true,
        options: {
          values: [
            'status',
            'connection_count',
            'cache_hit_ratio',
            'active_connections',
            'transactions_per_second',
            'queries_per_second',
            'index_hit_ratio',
            'slow_queries',
            'deadlocks'
          ]
        }
      },
      {
        name: 'condition',
        type: 'select',
        required: true,
        options: {
          values: ['=', '!=', '>', '<', '>=', '<=']
        }
      },
      {
        name: 'value',
        type: 'text',
        required: true
      },
      {
        name: 'severity',
        type: 'select',
        required: true,
        options: {
          values: ['info', 'warning', 'critical']
        }
      },
      {
        name: 'enabled',
        type: 'bool',
        required: true,
        options: {
          values: [true, false]
        }
      },
      {
        name: 'notification_channels',
        type: 'select',
        required: true,
        options: {
          values: ['email', 'webhook', 'in_app'],
          maxSelect: 3
        }
      },
      {
        name: 'webhook_url',
        type: 'text',
        required: false
      },
      {
        name: 'owner',
        type: 'relation',
        required: true,
        options: {
          collectionId: '_pb_users_auth_',
          cascadeDelete: false
        }
      }
    ],
    indexes: [
      'CREATE INDEX idx_alert_rules_database ON alert_rules (database)'
    ],
    listRule: '@request.auth.id = owner.id',
    viewRule: '@request.auth.id = owner.id',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = owner.id',
    deleteRule: '@request.auth.id = owner.id'
  });

  // Create alerts collection
  const alerts = new Collection({
    name: 'alerts',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'rule',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'alert_rules',
          cascadeDelete: true
        }
      },
      {
        name: 'database',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'monitored_databases',
          cascadeDelete: true
        }
      },
      {
        name: 'status',
        type: 'select',
        required: true,
        options: {
          values: ['triggered', 'acknowledged', 'resolved']
        }
      },
      {
        name: 'severity',
        type: 'select',
        required: true,
        options: {
          values: ['info', 'warning', 'critical']
        }
      },
      {
        name: 'message',
        type: 'text',
        required: true
      },
      {
        name: 'metric_value',
        type: 'text',
        required: true
      },
      {
        name: 'triggered_at',
        type: 'date',
        required: true
      },
      {
        name: 'acknowledged_at',
        type: 'date',
        required: false
      },
      {
        name: 'resolved_at',
        type: 'date',
        required: false
      },
      {
        name: 'acknowledged_by',
        type: 'relation',
        required: false,
        options: {
          collectionId: '_pb_users_auth_',
          cascadeDelete: false
        }
      }
    ],
    indexes: [
      'CREATE INDEX idx_alerts_database ON alerts (database)',
      'CREATE INDEX idx_alerts_rule ON alerts (rule)',
      'CREATE INDEX idx_alerts_status ON alerts (status)',
      'CREATE INDEX idx_alerts_triggered_at ON alerts (triggered_at)'
    ],
    listRule: '@request.auth.id = database.owner.id',
    viewRule: '@request.auth.id = database.owner.id',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = database.owner.id || @request.auth.id = acknowledged_by.id',
    deleteRule: '@request.auth.id = database.owner.id'
  });

  return {
    collections: {
      monitored_databases,
      database_status,
      performance_metrics,
      alert_rules,
      alerts
    }
  };
}, (db) => {
  // Revert the migration
  const collections = [
    'alerts',
    'alert_rules',
    'performance_metrics',
    'database_status',
    'monitored_databases'
  ];
  
  collections.forEach(collection => {
    db.deleteCollection(collection);
  });
});
