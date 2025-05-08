/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  // Create user_roles collection
  const roles = new Collection({
    name: 'user_roles',
    type: 'base',
    system: false,
    schema: [
      {
        name: 'name',
        type: 'text',
        required: true,
        options: {
          min: 2,
          max: 50
        }
      },
      {
        name: 'description',
        type: 'text',
        required: false
      },
      {
        name: 'permissions',
        type: 'json',
        required: true
      }
    ],
    indexes: [
      'CREATE UNIQUE INDEX idx_unique_role_name ON user_roles (name)'
    ],
    listRule: '@request.auth.id != ""',
    viewRule: '@request.auth.id != ""',
    createRule: '@request.auth.role.permissions.admin = true',
    updateRule: '@request.auth.role.permissions.admin = true',
    deleteRule: '@request.auth.role.permissions.admin = true'
  });

  // Add role field to users collection
  const users = db.collection('_pb_users_auth_');
  users.schema.push({
    name: 'role',
    type: 'relation',
    required: false,
    options: {
      collectionId: 'user_roles',
      cascadeDelete: false
    }
  });

  return {
    collections: {
      user_roles: roles,
      _pb_users_auth_: users
    }
  };
}, (db) => {
  // Remove role field from users collection
  const users = db.collection('_pb_users_auth_');
  const updatedSchema = users.schema.filter(field => field.name !== 'role');
  users.schema = updatedSchema;

  // Delete user_roles collection
  db.deleteCollection('user_roles');

  return {
    collections: {
      _pb_users_auth_: users
    }
  };
});
