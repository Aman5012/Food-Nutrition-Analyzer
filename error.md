# Current Bugs & Vulnerabilities

Here is a summary of the current bugs, architectural issues, and security vulnerabilities your project is currently facing, along with recommendations on how to fix them.

---

### 1. 🚨 CRITICAL: Compromised AWS SSH Key (`.pem` file)
* **The Bug:** Your `food-backend-key.pem` file was accidentally committed and pushed to your public GitHub repository. Even though we quickly deleted it, automated bots scrape GitHub constantly for these keys.
* **The Risk:** Anyone with this key can SSH into your EC2 instance, steal data, install malware, or use your server for crypto-mining (which can result in massive AWS bills).
* **The Fix:** 
  1. Terminate your current EC2 instance and launch a new one with a **brand-new Key Pair**.
  2. Alternatively, remove the compromised key from the `~/.ssh/authorized_keys` file on your EC2 instance and generate a new one.

---

### 2. ⚠️ Fragile IP Architecture (IP Address Changes)
* **The Bug:** Your AWS EC2 instance does not have a static IP. When you stop and start the instance, AWS assigns a completely new IP address (e.g., it changed from `54.226.24.55` to `3.83.184.237`).
* **The Risk:** Every time you restart the server, the frontend completely breaks because it is still trying to talk to the old IP. You have to manually update `vercel.json` and redeploy every single time.
* **The Fix:** Go to the AWS Console -> EC2 -> **Elastic IPs**. Allocate a new Elastic IP and attach it to your EC2 instance. This gives your server a permanent IP address that never changes.

---

### 3. ⚠️ Hardcoded Vercel Proxy & Mixed Content
* **The Bug:** Because your frontend is on Vercel (HTTPS) and your backend is on EC2 (HTTP), browsers block the connection. We fixed this by hardcoding the proxy in `vercel.json` to `http://3.83.184.237/api/:match*`.
* **The Risk:** While this works perfectly as a temporary fix, it is not ideal for production. If your Vercel deployment tries to proxy a massive image upload, it could hit Vercel's Edge Function timeout limits.
* **The Fix:** Buy a cheap domain name (e.g., `amanfoodai.com`), point it to your EC2 instance, and install a free Let's Encrypt SSL certificate using Nginx. Then you won't need the `vercel.json` proxy at all.

---

### 4. 🐛 Potential Backend API Key Missing (Edamam)
* **The Bug:** Your frontend `.env` has `EDAMAM_APP_ID` and `EDAMAM_APP_KEY`. However, these keys are actually used by your **backend** (in `app.py` for `get_nutrition_data_from_api`). 
* **The Risk:** When you deployed your Docker container on EC2, did you remember to copy your `.env` file to the server or pass the variables into Docker? If the backend is missing these keys, it will successfully identify the food, but it will **fail to fetch nutrition data** (calories, protein, etc.) and return empty values.
* **The Fix:** Ensure your `.env` file exists on your EC2 instance in the same folder as your `docker-compose.yml` or `Dockerfile`, and that Docker is configured to read it.

---

### 5. 🐛 Poor Frontend Error Handling
* **The Bug:** In `App.jsx`, when the backend returns an error (like `{"error": "No image file provided"}`), the frontend completely ignores the server's message.
* **The Risk:** It blindly throws a generic `"API error while analyzing image"`. This makes debugging extremely difficult because it hides the real reason the backend failed.
* **The Fix:** Update the `fetch` logic in `App.jsx` to parse the error message from the backend JSON and display it to the user.
