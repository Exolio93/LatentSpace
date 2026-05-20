# 🪐 Latent Space

*{{ data.introduction.welcome_word }}*

**La météo de la semaine :** {{ data.introduction.weather }}

{{ data.introduction.trend_summary }}

---

## 🏆 GRAND FORMAT : {{ data.top_news.title }}

**{{ data.top_news.catchphrase }}**

{{ data.top_news.trigger }}

{{ data.top_news.fact }}

**L'analyse Latent Space :**
*{{ data.top_news.big_picture }}*

{{ data.top_news.end_word }}

---

## 🚁 LE TOUR D'HORIZON

{% for item in data.news.items %}
### {{ item.catch_phrase }}
{{ item.content }}
{% endfor %}

---

## ⚡ EN BREF

{% for flash in data.flash_news.items %}
* **{{ flash.entity }}** : {{ flash.content }}
{% endfor %}

---
*Rédigé automatiquement par l'équipe d'agents IA de Latent Space.*