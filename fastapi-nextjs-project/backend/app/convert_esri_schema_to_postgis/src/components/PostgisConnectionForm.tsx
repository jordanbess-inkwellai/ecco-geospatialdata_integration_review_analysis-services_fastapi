import React from 'react';
import { useErdStore } from './ErdEditor';


const PostgisConnectionForm: React.FC = () => {
  const setPostgisHost = useErdStore((state) => state.setPostgisHost);
  const setPostgisDatabase = useErdStore((state) => state.setPostgisDatabase);
  const setPostgisUser = useErdStore((state) => state.setPostgisUser);
  const setPostgisPassword = useErdStore((state) => state.setPostgisPassword);
  const postgisHost = useErdStore((state) => state.postgisHost);
  const postgisDatabase = useErdStore((state) => state.postgisDatabase);
  const postgisUser = useErdStore((state) => state.postgisUser);
  const postgisPassword = useErdStore((state) => state.postgisPassword);


  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    console.log({ host: postgisHost, database: postgisDatabase, user: postgisUser, password: postgisPassword });

  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="host" className="block text-sm font-medium text-gray-700">
          Host
        </label>
        <input
          type="text"
          id="host"
          value={postgisHost}
          onChange={(e) => setPostgisHost(e.target.value)}
          required
          className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        />
      </div>
      <div>
        <label htmlFor="database" className="block text-sm font-medium text-gray-700">
          Database
        </label>
        <input
          type="text"
          id="database"
          value={postgisDatabase}
          onChange={(e) => setPostgisDatabase(e.target.value)}
          required
          className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        />
      </div>
      <div>
        <label htmlFor="user" className="block text-sm font-medium text-gray-700">
          User
        </label>
        <input
          type="text"
          id="user"
          value={postgisUser}
          onChange={(e) => setPostgisUser(e.target.value)}
          required
          className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        />
      </div>
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          type="password"
          id="password"
          value={postgisPassword}
          onChange={(e) => setPostgisPassword(e.target.value)}
          className="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        />
      </div>
      <button
        type="submit"
        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Submit
      </button>
    </form>
  );
};

export default PostgisConnectionForm;