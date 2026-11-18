# Connect Four web app

Play a full game against the final bot export. The app uses the original `bot_assets/code.zip` and `bot_assets/model.pt` together. The backend uses the export's CPU inference, search configuration, and game rules. Each browser session gets an independent board and search state.

## Run locally

Use Python 3.11 or 3.12 on Windows or Linux and run these commands from this directory.

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The first bot move of each game can take longer while the model loads.

## Publish on Streamlit Community Cloud

1. Push this directory's contents to the root of a dedicated GitHub repository on `main`. Keep `bot_assets/` and `.streamlit/` in the repository. Community Cloud can deploy from a private repository and make the app itself public.
2. On [Streamlit Community Cloud](https://share.streamlit.io/), select **Create app**, pick the repository and branch, and enter `app.py` as the main file. Select Python 3.12 in **Advanced settings**.
3. Set app visibility to **This app is public and searchable**. Open the assigned `streamlit.app` URL in a signed-out browser and play one move before sharing the link.

The free service may sleep after 12 hours of inactivity. Visitors can wake it from the page. Check access and move latency from the networks your players use before announcing the link.
