/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db);
  const roles = dao.findCollectionByNameOrId('user_roles');

  // Create Viewer role
  dao.saveRecord(new Record(roles, {
    name: 'Viewer',
    description: 'Can only view data, no modifications',
    permissions: JSON.stringify({
      view: true,
      create: false,
      update: false,
      delete: false,
      execute_query: false,
      upload: false,
      download: true,
      admin: false
    })
  }));

  // Create Analyst role
  dao.saveRecord(new Record(roles, {
    name: 'Analyst',
    description: 'Can run select queries but not modify data',
    permissions: JSON.stringify({
      view: true,
      create: false,
      update: false,
      delete: false,
      execute_query: true,
      upload: false,
      download: true,
      admin: false
    })
  }));

  // Create Project Manager role
  dao.saveRecord(new Record(roles, {
    name: 'Project Manager',
    description: 'Can make assignments and manage workflows but not modify data',
    permissions: JSON.stringify({
      view: true,
      create: false,
      update: {
        kestra_workflows: true,
        kestra_executions: true,
        kestra_triggers: true,
        monitored_databases: false,
        database_status: false,
        performance_metrics: false,
        alert_rules: true,
        alerts: true
      },
      delete: false,
      execute_query: true,
      upload: false,
      download: true,
      admin: false,
      manage_users: true,
      assign_tasks: true
    })
  }));

  // Create Data Engineer role
  dao.saveRecord(new Record(roles, {
    name: 'Data Engineer',
    description: 'Can upload and modify data',
    permissions: JSON.stringify({
      view: true,
      create: true,
      update: true,
      delete: {
        kestra_workflows: false,
        kestra_executions: false,
        kestra_triggers: false,
        monitored_databases: true,
        database_status: true,
        performance_metrics: true,
        alert_rules: true,
        alerts: true
      },
      execute_query: true,
      upload: true,
      download: true,
      admin: false,
      manage_users: false,
      assign_tasks: false
    })
  }));

  // Create Admin role
  dao.saveRecord(new Record(roles, {
    name: 'Admin',
    description: 'Full access to all features',
    permissions: JSON.stringify({
      view: true,
      create: true,
      update: true,
      delete: true,
      execute_query: true,
      upload: true,
      download: true,
      admin: true,
      manage_users: true,
      assign_tasks: true
    })
  }));

  return dao.getCollection('user_roles');
}, (db) => {
  const dao = new Dao(db);
  const roles = dao.findCollectionByNameOrId('user_roles');

  // Delete all roles
  const records = dao.findRecordsByFilter(roles.id, '');
  for (const record of records) {
    dao.deleteRecord(roles.id, record.id);
  }

  return dao.getCollection('user_roles');
});
