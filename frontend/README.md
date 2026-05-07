This is the Next.js frontend for Central Brain.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

1. Create a new Vercel project from this `frontend` folder.
2. Set the backend URL as an environment variable in Vercel:
	- `BACKEND_URL=https://your-backend-host.com`
	- `NEXT_PUBLIC_API_URL` is also supported for local development compatibility.
3. Deploy with the default Next.js build command: `npm run build`.

The frontend proxies its `/api/*` requests to the backend, so the browser stays on the same origin in production.
