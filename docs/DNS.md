# DNS Configuration for carprompt.co.uk

After deploying the frontend to Vercel, you'll need to point your domain to Vercel's servers.

## Step 1: Get Vercel DNS targets

Once the frontend is deployed, Vercel will provide two CNAME records:
- `cname.vercel-dns.com` (or similar)
- Possibly an A record for root domain (@)

You can find these in your Vercel project dashboard under **Domains**.

## Step 2: Log in to your domain registrar

Where did you buy carprompt.co.uk?
- GoDaddy
- Namecheap
- 123‑Reg / IONOS
- Google Domains
- Cloudflare
- Other

## Step 3: Add DNS records

Add the following records (replace with actual Vercel targets):

| Type  | Name                | Value                          | TTL   |
|-------|---------------------|--------------------------------|-------|
| CNAME | carprompt.co.uk     | cname.vercel-dns.com           | Auto  |
| CNAME | www.carprompt.co.uk | cname.vercel-dns.com           | Auto  |

**Note:** Some registrars require an A record for the root domain (@) instead of CNAME. Vercel will provide an IP address if needed.

## Step 4: Wait for propagation

DNS changes can take up to 48 hours to propagate globally, though usually within 1–2 hours.

## Step 5: Verify

Visit `https://carprompt.co.uk`. You should see the CarPrompt landing page.

## Email Forwarding (Optional)

Most registrars offer free email forwarding. Set up:

| Email                     | Forward to (your personal) |
|---------------------------|----------------------------|
| hello@carprompt.co.uk     | youremail@gmail.com        |
| contact@carprompt.co.uk   | youremail@gmail.com        |

## Troubleshooting

- **Domain not resolving:** Wait longer, clear DNS cache (`ipconfig /flushdns` on Windows, `sudo dscacheutil -flushcache` on macOS).
- **SSL not working:** Vercel automatically provisions SSL certificates once DNS is correctly pointed.
- **Backend not connecting:** Ensure `NEXT_PUBLIC_API_URL` environment variable in Vercel points to your Railway backend URL.