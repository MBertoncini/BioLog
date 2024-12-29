{% extends "mail_templated/base.tpl" %}

{% block subject %}
Conferma la tua email per Quiz Farfalle
{% endblock %}

{% block body %}
Ciao {{ user.username }},

Grazie per esserti registrato su Quiz Farfalle. Per completare la registrazione, clicca sul link seguente:

http://{{ domain }}{% url 'quiz_app:confirm_email' uidb64=uid token=token %}

Se non hai richiesto questa registrazione, ignora questa email.

Cordiali saluti,
Il team di Quiz Farfalle
{% endblock %}