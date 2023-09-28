from flask import Flask, request, redirect, session
import requests
import base64

app = Flask(__name__)

# Okta configuration
okta_client_id = "0oabkf2a5mazO52R65d7"
okta_client_secret = "5VD_KvJL3h_Y4crXgDU87GuDNbcOR-6SoIyvDUXsZVlToRPfo0CqhVhN0jaY0xGA" 
okta_redirect_uri = "http://localhost:8080/authorization-code/callback"

# Configura una clave secreta para la sesión
app.secret_key = '111'

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
    okta_token_url = "https://dev-95119950.okta.com/oauth2/default/v1/token"
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": okta_client_id,
        "client_secret": okta_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": okta_redirect_uri
    }

    response = requests.post(okta_token_url, headers=headers, data=data)

    # Verifica la respuesta y procesa el token si se obtiene correctamente
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        id_token = token_data.get("id_token")
        print(token_data)
        # Almacena el token de acceso en la sesión
        session['access_token'] = access_token
        session['id_token'] = id_token

        # Realiza una solicitud para obtener los datos del usuario
        userinfo_url = "https://dev-95119950.okta.com/oauth2/default/v1/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        userinfo_response = requests.get(userinfo_url, headers=headers)

        # Verifica la respuesta y muestra los datos del usuario si se obtienen correctamente
        if userinfo_response.status_code == 200:
            userinfo_data = userinfo_response.json()
            return f"<br>Datos del usuario: {userinfo_data}<br><a href='/logout'>Cerrar sesión</a>"
        else:
            return f"Error al obtener los datos del usuario: {userinfo_response.text}"
    else:
        return "Error al obtener el token de acceso desde Okta."

@app.route('/logout')
def logout():
    # Obtiene el token de acceso de la sesión
    access_token = session.get('access_token')
    id_token  =  session.get('id_token')
    if access_token:
        # Construye la URL de cierre de sesión de Okta
        okta_logout_url = f"https://dev-95119950.okta.com/oauth2/v1/logout?id_token_hint={id_token}&post_logout_redirect_uri={okta_redirect_uri}&state=someState"
        
        # Limpia la sesión
        session.clear()
        
        # Redirige al usuario a la URL de cierre de sesión de Okta
        return redirect(okta_logout_url)
    else:
        return "No hay sesión activa."


@app.route('/logout-complete')
def logout_complete():
    return "Sesión cerrada correctamente. <a href='/'>Volver a la página principal</a>"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
