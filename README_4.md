# workflow — Creative Portfolio Marketplace

Mobile-first portfolio directory for Artists, Graphic Designers, Architects and Developers. Creators can publish a profile, showcase projects/services/digital products, set prices and share direct contact links. Payments are arranged directly between the creator and client; this project does not collect payments or take commission.

## Preview
Open `index.html` through a local web server. The page shows sample profiles until Firebase is configured. For Firebase module imports, use a local server rather than opening the file as `file://`.

## Firebase setup (free tier may have limits)
1. Open https://console.firebase.google.com/ and create a project named `workflow` (or your preferred ID).
2. Add a **Web app** and copy its config into `firebase-config.js`.
3. In **Authentication → Sign-in method**, enable Email/Password.
4. In **Firestore Database**, create a database.
5. In **Storage**, create a bucket. Depending on current Firebase billing/policy, Storage may require a billing-enabled plan; check Firebase Console before relying on free uploads.
6. In Firestore → Rules, paste `firestore.rules` and publish. In Storage → Rules, paste `storage.rules` and publish.
7. For a live deployment, use a static host (Vercel, Netlify, Firebase Hosting, or GitHub Pages). Since Firebase browser SDK imports use HTTPS, the deployed site must use HTTPS.

## Make yourself the admin
1. Create your account on the website.
2. In Firebase Console → Authentication → Users, copy your account's UID.
3. In Firestore, create a collection named `admins` and a document whose ID is exactly your UID (fields can include `createdAt` timestamp).
4. Only trusted project owners should create documents in `admins`. The client cannot create or edit admin records.
5. Sign in on the website, then open `https://YOUR_SITE_URL/#admin`. The Admin page can moderate profiles. The Firestore rules are the security boundary; hiding a button is not security.

## Publish with GitHub + Vercel from a phone
1. Extract this ZIP.
2. Create a GitHub repository named `workflow`.
3. Upload all files from this folder (not the outer folder itself if GitHub's uploader makes nested folders).
4. Open https://vercel.com/, import the repository, keep Framework Preset as **Other**, Build Command empty, Output Directory `.` (or leave defaults for a static site), then deploy.
5. Configure Firebase Authentication → Settings → Authorized domains with your Vercel domain.
6. Test account registration, profile publishing, image/video upload, direct contact, and admin access.

## Data and security notes
- `firebase-config.js` contains public Firebase web-app identifiers, not a private server key. Never upload service-account JSON or private credentials.
- Firestore rules restrict profile editing and project creation to the signed-in owner. Public reads are limited to published profiles/projects.
- This starter uses public portfolio media. Do not upload private documents, source files that should be paid downloads, or sensitive personal information. Digital product links currently point to external URLs; protected paid downloads need a backend and a secure delivery system.
- WhatsApp numbers are public if added. Only enter contact details you intend to share.
- Direct payment means clients pay creators outside this site. This project does not verify payment, provide escrow, handle refunds, or guarantee a creator's work.
- Admin moderation in this starter is basic. For production use, consider App Check, rate limiting, server-side validation, abuse reporting, account deletion flow, backups, and stronger admin custom claims.
- Demo mode does not save data online. Configure Firebase to enable real accounts and uploads.
