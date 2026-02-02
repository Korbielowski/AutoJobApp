import { MetaProvider, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";
import { Suspense } from "solid-js";
import createClient from "openapi-fetch";
import { paths } from "../api/api";
import  NavBar  from "~/components/NavBar";
import "./app.css";

const client = createClient<paths>({baseUrl: "http://127.0.0.1:8000/"});

export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          <Title>SolidStart - Basic</Title>
            <NavBar/>
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
