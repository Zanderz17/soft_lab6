from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

# Datos de configuración de la aplicación Okta
okta_client_id = "0oabkf2a5mazO52R65d7"
okta_client_secret = "5VD_KvJL3h_Y4crXgDU87GuDNbcOR-6SoIyvDUXsZVlToRPfo0CqhVhN0jaY0xGA" 
okta_redirect_uri = "http://localhost:8080/authorization-code/callback"

@app.route('/')
def root():
    # Redirige a la URL de autorización de Okta
    return redirect("https://dev-95119950.okta.com/oauth2/default/v1/authorize?scope=openid%20email%20profile&response_type=code&state=abcdefgh&client_id=" + okta_client_id + "&redirect_uri=" + okta_redirect_uri)

@app.route('/authorization-code/callback')
def authorization_callback():
    # Obtiene el código y el estado del parámetro de la URL de retorno
    code = request.args.get("code")
    state = request.args.get("state")

    # Realiza el POST a la URL de Okta para obtener el token de acceso
    okta_token_url = "https://dev-16281537.okta.com/oauth2/default/v1/token"
    headers = {
        "Authorization": base64.b64encode((okta_client_id + "," + okta_client_secret)).encode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": okta_redirect_uri
    }

    response = requests.post(okta_token_url, headers=headers, params=params)

    # Verifica la respuesta y procesa el token si se obtiene correctamente
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        return f"Token de acceso obtenido exitosamente: {access_token}"
    else:
        return "Error al obtener el token de acceso desde Okta."

if __name__ == '__main__':
    app.run(debug=True, port=8080)
