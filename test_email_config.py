from app.services.email_service import email_service

# Prueba con TU email personal para verificar que llega
result = email_service.send_password_changed(
    user_email="mdsolis@unibarranquilla.edu.co",  # ⬅️ Cambia esto por tu email
    user_name="Usuario Prueba",
    changed_by="Sistema"
)

if result:
    print("✅ Email enviado correctamente!")
    print("📧 Revisa tu bandeja de entrada")
else:
    print("❌ Error al enviar email")
    print("Revisa las credenciales en .env")