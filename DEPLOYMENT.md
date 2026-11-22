# Deploy Scanner 5.0 dashboard on Render and Streamlit

The repository includes a shared Streamlit dashboard entry point for both hosting platforms.

## Streamlit Community Cloud
1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Select repository nsdlshahpur-wq/Scanner-5.0.
3. Select branch main after the dashboard PR is merged.
4. Set Main file path to scanner-core/trader-india/web-dashboard/streamlit_app.py.
5. Deploy. Dependencies are read from scanner-core/trader-india/web-dashboard/requirements.txt.

## Render
1. Open https://dashboard.render.com/ and choose New → Blueprint.
2. Connect nsdlshahpur-wq/Scanner-5.0 and select main.
3. Render reads the root render.yaml and creates the Streamlit web service.
4. Wait for deployment and open the generated onrender.com URL.

## Dashboard usage
Generate scanner JSON outputs using commands in scanner-core/README.md, then upload one or more JSON files in the app sidebar. The dashboard supports US, NSE, BSE and other market labels inferred from filenames.

This repository change prepares both deployment targets. It cannot authorize or deploy into the user's Render or Streamlit account; the user must connect the repository and approve hosting from those services. The dashboard is upload-based and read-only: it does not independently verify live prices or place orders.
