/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  // Create kestra_workflows collection
  const kestra_workflows = new Collection({
    name: 'kestra_workflows',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'name',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 200
        }
      },
      {
        name: 'namespace',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'workflow_id',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'description',
        type: 'text',
        required: false
      },
      {
        name: 'tags',
        type: 'json',
        required: false
      },
      {
        name: 'triggers',
        type: 'json',
        required: false
      },
      {
        name: 'tasks',
        type: 'json',
        required: false
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
      'CREATE UNIQUE INDEX idx_unique_workflow ON kestra_workflows (namespace, workflow_id)'
    ],
    listRule: '@request.auth.id != ""',
    viewRule: '@request.auth.id != ""',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = owner.id',
    deleteRule: '@request.auth.id = owner.id'
  });

  // Create kestra_executions collection
  const kestra_executions = new Collection({
    name: 'kestra_executions',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'workflow',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'kestra_workflows',
          cascadeDelete: true
        }
      },
      {
        name: 'execution_id',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'namespace',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'workflow_id',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 100
        }
      },
      {
        name: 'status',
        type: 'select',
        required: true,
        options: {
          values: ['CREATED', 'RUNNING', 'PAUSED', 'RESTARTED', 'KILLING', 'SUCCESS', 'WARNING', 'FAILED', 'KILLED']
        }
      },
      {
        name: 'start_date',
        type: 'date',
        required: false
      },
      {
        name: 'end_date',
        type: 'date',
        required: false
      },
      {
        name: 'duration',
        type: 'number',
        required: false
      },
      {
        name: 'inputs',
        type: 'json',
        required: false
      },
      {
        name: 'outputs',
        type: 'json',
        required: false
      },
      {
        name: 'task_runs',
        type: 'json',
        required: false
      },
      {
        name: 'trigger',
        type: 'json',
        required: false
      }
    ],
    indexes: [
      'CREATE UNIQUE INDEX idx_unique_execution ON kestra_executions (execution_id)',
      'CREATE INDEX idx_execution_workflow ON kestra_executions (workflow)',
      'CREATE INDEX idx_execution_status ON kestra_executions (status)',
      'CREATE INDEX idx_execution_dates ON kestra_executions (start_date, end_date)'
    ],
    listRule: '@request.auth.id != ""',
    viewRule: '@request.auth.id != ""',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id != ""',
    deleteRule: '@request.auth.id = workflow.owner.id'
  });

  // Create kestra_triggers collection
  const kestra_triggers = new Collection({
    name: 'kestra_triggers',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'name',
        type: 'text',
        required: true,
        options: {
          min: 1,
          max: 200
        }
      },
      {
        name: 'workflow',
        type: 'relation',
        required: true,
        options: {
          collectionId: 'kestra_workflows',
          cascadeDelete: true
        }
      },
      {
        name: 'trigger_type',
        type: 'select',
        required: true,
        options: {
          values: ['pocketbase_event', 'database_alert', 'schedule', 'webhook', 'manual']
        }
      },
      {
        name: 'collection',
        type: 'text',
        required: false
      },
      {
        name: 'event_type',
        type: 'select',
        required: false,
        options: {
          values: ['create', 'update', 'delete', 'alert']
        }
      },
      {
        name: 'filter',
        type: 'text',
        required: false
      },
      {
        name: 'schedule',
        type: 'text',
        required: false
      },
      {
        name: 'inputs',
        type: 'json',
        required: false
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
        name: 'last_triggered',
        type: 'date',
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
      'CREATE INDEX idx_trigger_workflow ON kestra_triggers (workflow)',
      'CREATE INDEX idx_trigger_type ON kestra_triggers (trigger_type)',
      'CREATE INDEX idx_trigger_collection ON kestra_triggers (collection)'
    ],
    listRule: '@request.auth.id != ""',
    viewRule: '@request.auth.id != ""',
    createRule: '@request.auth.id != ""',
    updateRule: '@request.auth.id = owner.id',
    deleteRule: '@request.auth.id = owner.id'
  });

  return {
    collections: {
      kestra_workflows,
      kestra_executions,
      kestra_triggers
    }
  };
}, (db) => {
  // Revert the migration
  const collections = [
    'kestra_triggers',
    'kestra_executions',
    'kestra_workflows'
  ];
  
  collections.forEach(collection => {
    db.deleteCollection(collection);
  });
});
