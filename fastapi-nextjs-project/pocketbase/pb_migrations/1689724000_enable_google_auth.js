/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db);
  
  // Get the auth collection
  const collection = dao.findCollectionByNameOrId("_pb_users_auth_");
  
  // Update the auth options to enable Google auth
  return dao.saveCollection(collection.$updateAuthOptions({
    "authProviders": [
      {
        "name": "google",
        "state": "enabled",
        "options": {
          "clientId": "{{GOOGLE_CLIENT_ID}}",
          "clientSecret": "{{GOOGLE_CLIENT_SECRET}}",
          "authUrl": "https://accounts.google.com/o/oauth2/auth",
          "tokenUrl": "https://oauth2.googleapis.com/token",
          "userApiUrl": "https://www.googleapis.com/oauth2/v1/userinfo",
          "userApiFields": {
            "id": "id",
            "name": "name",
            "username": "email",
            "email": "email",
            "avatarUrl": "picture"
          }
        }
      }
    ]
  }));
}, (db) => {
  const dao = new Dao(db);
  
  // Get the auth collection
  const collection = dao.findCollectionByNameOrId("_pb_users_auth_");
  
  // Revert the auth options to disable Google auth
  return dao.saveCollection(collection.$updateAuthOptions({
    "authProviders": []
  }));
});
