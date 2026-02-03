import type {paths} from "./api";
import createClient from "openapi-fetch";

export const client = createClient<paths>({baseUrl: "http://127.0.0.1:8000/"})