import {useLocation} from "react-router-dom";

export function useQuery() {
  return new URLSearchParams(window.location.search);
}