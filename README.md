原作者https://github.com/Jaammerr/The-Dawn-Bot
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

wget -O Dawn.sh https://raw.githubusercontent.com/sdohuajia/Dawn/refs/heads/main/Dawn.sh && sed -i 's/\r$//' Dawn.sh && chmod +x Dawn.sh && ./Dawn.sh

