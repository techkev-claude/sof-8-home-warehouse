"""KI-Provider-Stub.

Die eigentliche Bilderkennung (Kabeltyp/Stecker) laeuft On-Device in der
Android-App (siehe ANDROID_INTEGRATION.md) - das Backend ruft fuer v1 keine
KI selbst auf. Dieses Modul bleibt als Erweiterungspunkt bestehen, falls
spaeter zusaetzlich ein serverseitiger/Cloud-Provider angebunden werden soll
(z.B. fuer Web-UI-Uploads ohne App). Neuer Provider = neue Funktion hier,
kein Umbau der Router noetig.
"""

from typing import Optional
from app.config import settings


class AIAnalysisResult:
    def __init__(
        self,
        name: str,
        description: str,
        connector_a: Optional[str],
        connector_b: Optional[str],
        confidence: float,
        raw: str,
    ):
        self.name = name
        self.description = description
        self.connector_a = connector_a
        self.connector_b = connector_b
        self.confidence = confidence
        self.raw = raw


async def analyze_cable_image(image_path: str) -> Optional[AIAnalysisResult]:
    if settings.ai_provider == "none":
        return None
    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
