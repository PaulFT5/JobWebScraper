import {fetchFilters} from "$lib/api/fetchFilters";

export const load = async ({ fetch }) => fetchFilters(fetch);