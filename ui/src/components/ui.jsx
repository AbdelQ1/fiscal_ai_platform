import React from "react";

export function Page({ children }) {
  return <div className="container">{children}</div>;
}

export function Card({ title, right, children }) {
  return (
    <section className="card">
      <div className="card__header">
        <h2 className="m-0">{title}</h2>
        {right}
      </div>
      <div>{children}</div>
    </section>
  );
}

export function Button({ children, onClick, variant = "primary" }) {
  const cls = `btn ${variant === "ghost" ? "btn--ghost" : "btn--primary"}`;
  return (
    <button onClick={onClick} className={cls}>
      {children}
    </button>
  );
}

export function Badge({ children, ok=false, failed=false, loading=false }) {
  const cls =
    "badge " +
    (ok ? "badge--ok" : failed ? "badge--failed" : loading ? "badge--load" : "badge--load");
  return <span className={cls}>{children}</span>;
}
