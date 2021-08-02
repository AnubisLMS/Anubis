export const useQuery = (search) => {
  if (!search) return null;
  const query = search.substr(1, search.length).split('=');
  const queryParams = {};
  queryParams[query[0]] =
    query[1].toLowerCase() === 'true'
      ? true
      : query[1].toLowerCase() === 'false'
      ? false
      : query[1];
  return queryParams;
};
