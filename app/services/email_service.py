from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "MediVision")
        
    def _get_base_template(self, title: str, content: str) -> str:
        """Plantilla HTML base para todos los correos"""
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info-box strong {{
                    color: #667eea;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
                .alert {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 {self.from_name}</h1>
                </div>
                <div class="content">
                    <h2>{title}</h2>
                    {content}
                </div>
                <div class="footer">
                    <p>Este es un correo automático, por favor no responder.</p>
                    <p>© 2025 {self.from_name}. Todos los derechos reservados.</p>
                    <p><small>Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envía un correo electrónico"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email enviado a {to_email}: {subject}")
            return True
        except Exception as e:
            print(f"❌ Error enviando email a {to_email}: {str(e)}")
            return False
    
    # ========================================
    # NOTIFICACIONES DE CAMBIOS DE PERFIL
    # ========================================
    
    def send_password_changed(self, user_email: str, user_name: str, changed_by: str) -> bool:
        """Notificación de cambio de contraseña"""
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>Te informamos que tu contraseña ha sido modificada exitosamente.</p>
        
        <div class="info-box">
            <strong>📅 Fecha del cambio:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
            <strong>👤 Modificado por:</strong> {changed_by}
        </div>
        
        <div class="alert">
            <strong>⚠️ Importante:</strong> Si no realizaste este cambio, por favor contacta con el administrador inmediatamente.
        </div>
        
        <p>Por seguridad, se recomienda:</p>
        <ul>
            <li>Usar una contraseña fuerte y única</li>
            <li>No compartir tus credenciales</li>
            <li>Cerrar sesión en dispositivos compartidos</li>
        </ul>
        """
        
        html = self._get_base_template("🔐 Cambio de Contraseña", content)
        return self._send_email(user_email, "Tu contraseña ha sido modificada - MediVision", html)
    
    def send_profile_updated(self, user_email: str, user_name: str, changes: Dict, changed_by: str) -> bool:
        """Notificación de actualización de perfil"""
        changes_html = ""
        field_names = {
            'full_name': 'Nombre completo',
            'last_name': 'Apellido',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'email': 'Correo electrónico',
            'genero': 'Género',
            'date_birth': 'Fecha de nacimiento'
        }
        
        for field, value in changes.items():
            changes_html += f"<li><strong>{field_names.get(field, field)}:</strong> {value['new']}</li>"
        
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>Tu información personal ha sido actualizada en el sistema.</p>
        
        <div class="info-box">
            <strong>📝 Cambios realizados:</strong>
            <ul style="margin: 10px 0;">
                {changes_html}
            </ul>
            <strong>📅 Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
            <strong>👤 Modificado por:</strong> {changed_by}
        </div>
        
        <div class="alert">
            <strong>⚠️ Atención:</strong> Si no reconoces estos cambios, contacta al administrador.
        </div>
        """
        
        html = self._get_base_template("✏️ Perfil Actualizado", content)
        return self._send_email(user_email, "Tu perfil ha sido actualizado - MediVision", html)
    
    # ========================================
    # NOTIFICACIONES DE CITAS
    # ========================================
    
    def send_appointment_status_changed(
        self, 
        user_email: str, 
        user_name: str,
        appointment_date: str,
        old_status: str,
        new_status: str,
        changed_by: str,
        doctor_name: Optional[str] = None
    ) -> bool:
        """Notificación de cambio de estado de cita"""
        
        status_colors = {
            'Confirmada': '#28a745',
            'Pendiente': '#ffc107',
            'Cancelada': '#dc3545',
            'Completada': '#17a2b8'
        }
        
        status_icons = {
            'Confirmada': '✅',
            'Pendiente': '⏳',
            'Cancelada': '❌',
            'Completada': '✔️'
        }
        
        color = status_colors.get(new_status, '#667eea')
        icon = status_icons.get(new_status, '📋')
        
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>El estado de tu cita médica ha sido actualizado.</p>
        
        <div class="info-box">
            <strong>📅 Fecha de la cita:</strong> {appointment_date}<br>
            {f'<strong>👨‍⚕️ Doctor:</strong> {doctor_name}<br>' if doctor_name else ''}
            <strong>Estado anterior:</strong> <span style="color: {status_colors.get(old_status, '#666')}">{status_icons.get(old_status, '•')} {old_status}</span><br>
            <strong>Nuevo estado:</strong> <span style="color: {color}; font-weight: bold;">{icon} {new_status}</span><br>
            <strong>Modificado por:</strong> {changed_by}<br>
            <strong>Fecha del cambio:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """
        
        if new_status == 'Cancelada':
            content += """
            <div class="alert">
                <strong>ℹ️ Nota:</strong> Si deseas reagendar tu cita, por favor comunícate con la secretaría.
            </div>
            """
        elif new_status == 'Confirmada':
            content += """
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <strong>✅ ¡Cita confirmada!</strong> Por favor asiste puntualmente a tu cita.
            </div>
            """
        
        html = self._get_base_template(f"{icon} Estado de Cita Actualizado", content)
        return self._send_email(user_email, f"Cambio de estado de cita - {new_status}", html)
    
    def send_new_appointment(
        self,
        user_email: str,
        user_name: str,
        appointment_date: str,
        doctor_name: str,
        created_by: str
    ) -> bool:
        """Notificación de nueva cita agendada"""
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>Se ha agendado una nueva cita médica para ti.</p>
        
        <div class="info-box">
            <strong>📅 Fecha y hora:</strong> {appointment_date}<br>
            <strong>👨‍⚕️ Doctor:</strong> {doctor_name}<br>
            <strong>📍 Estado:</strong> <span style="color: #ffc107">⏳ Pendiente</span><br>
            <strong>Agendada por:</strong> {created_by}<br>
            <strong>Fecha de registro:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        
        <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <strong>💡 Recordatorio:</strong> Por favor confirma tu asistencia con anticipación.
        </div>
        """
        
        html = self._get_base_template("📅 Nueva Cita Agendada", content)
        return self._send_email(user_email, "Nueva cita médica agendada - MediVision", html)
    
    # ========================================
    # NOTIFICACIONES DE ANÁLISIS
    # ========================================
    
    def send_analysis_status_changed(
        self,
        user_email: str,
        user_name: str,
        analysis_type: str,
        old_status: str,
        new_status: str,
        changed_by: str
    ) -> bool:
        """Notificación de cambio de estado de análisis"""
        
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>El estado de tu análisis clínico ha sido actualizado.</p>
        
        <div class="info-box">
            <strong>🔬 Tipo de análisis:</strong> {analysis_type}<br>
            <strong>Estado anterior:</strong> {old_status}<br>
            <strong>Nuevo estado:</strong> <span style="color: #28a745; font-weight: bold;">✅ {new_status}</span><br>
            <strong>Actualizado por:</strong> {changed_by}<br>
            <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """
        
        if new_status.lower() in ['completado', 'listo', 'finalizado']:
            content += """
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <strong>✅ ¡Resultados disponibles!</strong> Ya puedes consultar tus resultados en la plataforma.
            </div>
            """
        
        html = self._get_base_template("🔬 Estado de Análisis Actualizado", content)
        return self._send_email(user_email, "Actualización de análisis clínico - MediVision", html)
    
    def send_analysis_uploaded_confirmation(
        self,
        user_email: str,
        user_name: str,
        analysis_id: int,
        upload_date: str
    ) -> bool:
        """Confirmación de carga de análisis exitosa"""
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>Hemos recibido tu imagen para análisis clínico exitosamente.</p>
        
        <div class="info-box">
            <strong>📋 ID de análisis:</strong> #{analysis_id}<br>
            <strong>📅 Fecha de carga:</strong> {upload_date}<br>
            <strong>📍 Estado inicial:</strong> <span style="color: #ffc107">⏳ En proceso</span>
        </div>
        
        <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <strong>ℹ️ ¿Qué sigue?</strong><br>
            • Nuestro equipo médico revisará tu imagen<br>
            • Te notificaremos cuando los resultados estén listos<br>
            • Podrás consultar el estado en tu panel de paciente
        </div>
        
        <p>El tiempo estimado de procesamiento es de <strong>24-48 horas</strong>.</p>
        
        <p style="margin-top: 30px; color: #666; font-size: 14px;">
            Si tienes alguna pregunta, no dudes en contactar con nosotros.
        </p>
        """
        
        html = self._get_base_template("✅ Análisis Recibido", content)
        return self._send_email(user_email, "Confirmación de carga de análisis - MediVision", html)
    
    # ========================================
    # NOTIFICACIONES PARA DOCTORES/SECRETARIOS
    # ========================================
    
    def send_role_changed(
        self,
        user_email: str,
        user_name: str,
        old_role: str,
        new_role: str,
        changed_by: str
    ) -> bool:
        """Notificación de cambio de rol"""
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>Tu rol en el sistema ha sido modificado.</p>
        
        <div class="info-box">
            <strong>Rol anterior:</strong> {old_role}<br>
            <strong>Nuevo rol:</strong> <span style="color: #667eea; font-weight: bold;">{new_role}</span><br>
            <strong>Modificado por:</strong> {changed_by}<br>
            <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        
        <div class="alert">
            <strong>ℹ️ Importante:</strong> Tus permisos y accesos en el sistema han cambiado según tu nuevo rol.
        </div>
        
        <p>Por favor, cierra sesión y vuelve a iniciar para que los cambios tomen efecto.</p>
        """
        
        html = self._get_base_template("🔄 Cambio de Rol", content)
        return self._send_email(user_email, "Tu rol ha sido actualizado - MediVision", html)
    
    def send_account_status_changed(
        self,
        user_email: str,
        user_name: str,
        is_active: bool,
        changed_by: str
    ) -> bool:
        """Notificación de activación/desactivación de cuenta"""
        
        if is_active:
            title = "✅ Cuenta Activada"
            message = "Tu cuenta ha sido <strong style='color: #28a745'>activada</strong> exitosamente."
            note = "Ya puedes acceder al sistema con normalidad."
            note_style = "background: #d4edda; border-left: 4px solid #28a745;"
        else:
            title = "⚠️ Cuenta Desactivada"
            message = "Tu cuenta ha sido <strong style='color: #dc3545'>desactivada</strong> temporalmente."
            note = "No podrás acceder al sistema hasta que tu cuenta sea reactivada."
            note_style = "background: #f8d7da; border-left: 4px solid #dc3545;"
        
        content = f"""
        <p>Hola <strong>{user_name}</strong>,</p>
        <p>{message}</p>
        
        <div class="info-box">
            <strong>Estado:</strong> {'Activa' if is_active else 'Inactiva'}<br>
            <strong>Modificado por:</strong> {changed_by}<br>
            <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        
        <div style="{note_style} padding: 15px; margin: 20px 0; border-radius: 4px;">
            <strong>ℹ️ Nota:</strong> {note}
        </div>
        
        <p>Si tienes preguntas, contacta al administrador del sistema.</p>
        """
        
        html = self._get_base_template(title, content)
        return self._send_email(user_email, "Estado de cuenta actualizado - MediVision", html)

# Instancia global del servicio
email_service = EmailService()
