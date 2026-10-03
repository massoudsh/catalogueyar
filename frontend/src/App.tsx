import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Atmosphere } from "./components/Atmosphere";
import { SiteHeader } from "./components/SiteHeader";
import { checkHealth } from "./lib/api";
import { HomePage } from "./pages/HomePage";
import { WorkspacePage } from "./pages/WorkspacePage";

export function App() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    void checkHealth().then((ok) => {
      if (!cancelled) setApiOnline(ok);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <BrowserRouter>
      <Atmosphere>
        <SiteHeader apiOnline={apiOnline} />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
        </Routes>
      </Atmosphere>
    </BrowserRouter>
  );
}
