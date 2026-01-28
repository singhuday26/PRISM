import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { ErrorBoundary } from "../ErrorBoundary";

export function Layout() {
    return (
        <div
            style={{
                display: "flex",
                minHeight: "100vh",
                width: "100%",
                backgroundColor: "#0f172a",
            }}
        >
            <Sidebar />

            <div className="flex-1 flex flex-col">
                <Header />

                <main className="flex-1 p-6 overflow-auto">
                    <ErrorBoundary>
                        <Outlet />
                    </ErrorBoundary>
                </main>
            </div>
        </div>
    );
}
