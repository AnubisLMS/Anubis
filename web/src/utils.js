
export function useQuery() {
  return new URLSearchParams(window.location.search);
}