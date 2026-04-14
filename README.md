# Avertizare meteorologica ANM Home Assistant
Integrare avertizari meteo in Home Assistant

1. Despre

Integrarea foloseste API ANM de pe site-ul https://www.meteoromania.ro/ pentru a prelua atentionarile meteorologice.

2. Instalare
   - Descarcati acest repository in format zip.
   - Copiati folderul alerta_anm in folderul /config/custom_components din Home Assistant
   - Reporniti Home Assistant
   - Adaugati integrarea din Settings > Devices & Services > Integrations > Add Integration

3. Configurare

Componenta va crea automat 2 senzori pentru fiecare judet selectat, binary_sensor.avertizare_anm_judet si sensor.avertizare_anm_judet
Se pot adauga oricate judete doriti din configurarea integrarii.
Se poate seta intervalul de preluare al datelor (Implicit; 15 minute).
Senzorul binar este de tip safety si poate fi folosit ca trigger pentru automatizari.

3. Prelucrarea datelor

Datele pot fi extrase din senzorul integrarii si pot fi folosite in dashboard sau automatizari.

Exemplu dashboard simplu:

	type: markdown
    title: ⛈️ Avertizări Meteo ANM
    content: |2-
      {% set avertizari = state_attr('sensor.avertizare_anm_cs', 'avertizari') %}
      {% if avertizari %}
      {% for alerta in avertizari %}
      ### ⚠️ Cod {{ alerta.stare | capitalize }}
      **Fenomene:** {{ alerta.fenomeneVizate }}
    
      **Valabilitate:** {{ alerta.dataAparitiei }} – {{ alerta.dataExpirarii }}

      {{ alerta.mesaj }}
    
      ---
      {% endfor %}
      {% else %}
      ✅ Momentan nu există avertizări meteorologice pentru acest județ.
      {% endif %}

![Preview](https://raw.githubusercontent.com/aurelmarius/avertizare-anm-ha/refs/heads/main/.github/img/anm_dash.png)

Exemplu automatizare:

```
alias: "Notificare Avertizare Meteo ANM"
description: "Trimite notificare pe telefon cand apare o noua avertizare"
mode: single
trigger:
  - platform: state
    entity_id: binary_sensor.avertizare_anm_cs # Inlocuieste binary_sensor.avertizare_anm_cs cu numele senzorului tau
    from: "off"
    to: "on"
action:
  - service: notify.mobile_app_test # Inlocuieste cu numele deviceului tau
    data:
      title: "⚠️ Alertă Meteo Nouă!"
      message: >-
        {% set avertizari = state_attr('sensor.avertizare_anm_cs', 'avertizari') %} # Inlocuieste sensor.avertizare_anm_cs cu numele senzorului tau
        {% if avertizari %}
          S-au emis următoarele avertizări:
          {% for alerta in avertizari %}
            - Cod {{ alerta.stare | capitalize }}: {{ alerta.fenomeneVizate }}
          {% endfor %}
          Verifică aplicația pentru detalii complete.
        {% else %}
          S-a emis o alertă, dar detaliile nu sunt disponibile.
        {% endif %}
```
