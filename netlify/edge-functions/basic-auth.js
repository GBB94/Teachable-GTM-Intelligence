// HTTP Basic Auth gate for the whole site.
// Netlify's `[[headers]] Basic-Auth` directive is a no-op, so enforcement
// lives here in an edge function (free tier, runs on every request).
export default async (request, context) => {
  const USER = "teachable";
  const PASS = "Teachable2026!";
  const expected = "Basic " + btoa(`${USER}:${PASS}`);

  const provided = request.headers.get("authorization") || "";
  if (provided !== expected) {
    return new Response("Authentication required.", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="Teachable GTM Intelligence", charset="UTF-8"',
        "Content-Type": "text/plain; charset=UTF-8",
      },
    });
  }

  return context.next();
};

export const config = { path: "/*" };
