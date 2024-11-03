# Dawn Extension Bot [1.5]

致谢 https://github.com/Jaammerr/The-Dawn-Bot
主要是在这位大佬的基础上完成了验证码自动识别，不需要付费打码

![img.png](img.png)

家人们 要点赞 要关注哦
---

## 🚀 Features

- ✅ Automatic account registration and login
- 📧 Automated account reverification
- 🌾 Automated completion of all tasks
- 💰 Automated farming of points
- 📊 Export account statistics
- 🔄 Keepalive functionality to maintain session
- 🧩 Advanced captcha solving

---

## 💻 Requirements

- Python >= 3.11
- Internet connection
- Valid email accounts for registration
- Valid proxies (optional)

---

## 🛠️ Setup

1. Clone the repository:
   ```bash
   git clone [repository URL]
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   cd venv/Scripts
   activate
   cd ../..
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

### settings.yaml

This file contains general settings for the bot:

```yaml
threads: 5 # Number of threads for simultaneous account operations
keepalive_interval: 120 # Delay between keepalive requests in seconds
referral_code: "YOUR_REFERRAL_CODE" # Referral code for registration
captcha_service: "2captcha" # Service for solving captcha (2captcha or anticaptcha)
two_captcha_api_key: "YOUR_2CAPTCHA_API_KEY"
anti_captcha_api_key: "YOUR_ANTICAPTCHA_API_KEY"

imap_settings: # IMAP settings for email providers
  gmail.com: imap.gmail.com
  outlook.com: imap-mail.outlook.com
  # Add more email providers as needed
```

### Other Configuration Files

#### 📁 register.txt
Contains accounts for registration.
```
Format:
email:password
email:password
...
```

#### 📁 farm.txt
Contains accounts for farming and task completion.
```
Format:
email:password
email:password
...
```

#### 📁 proxies.txt
Contains proxy information.
```
Format:
http://user:pass@ip:port
http://ip:port:user:pass
http://ip:port@user:pass
http://user:pass:ip:port
...
```

---

## 🚀 Usage

1. Ensure all configuration files are set up correctly.
2. Run the bot:
   ```bash
   python run.py
   ```

---

## ⚠️ Important Notes

- The recommended delay between keepalive requests is 120 seconds.
- If you have unverified accounts, you can use the `register` module again to reverify them.
- Captcha solving now uses external services (2captcha, anti-captcha) due to changes in captcha complexity.
- A database is used to optimize login processes by storing authorization tokens.
- For email services like Gmail, you may need to use application-specific passwords instead of regular email passwords.

---

## 🔧 Troubleshooting

- **Email Verification Issues**: Check your email provider's IMAP settings in `settings.yaml`.
- **Captcha Problems**: Verify your captcha service API key and account balance.
- **Proxy Issues**: Ensure your proxy format is correct and the proxies are functional.

---