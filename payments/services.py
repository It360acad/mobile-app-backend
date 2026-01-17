import requests
from django.conf import settings
from typing import Dict, Optional

class PaystackService:
  BASE_URL = 'https://api.paystack.co'
   
  def __init__(self):
    # Validate secret key is set
    if not hasattr(settings, 'PAYSTACK_SECRET_KEY') or not settings.PAYSTACK_SECRET_KEY:
      raise ValueError(
        "PAYSTACK_SECRET_KEY is not configured. "
        "Set PAYSTACK_SECRET_KEY in your environment variables."
      )
    
    self.secret_key = settings.PAYSTACK_SECRET_KEY
    
    # Never expose secret key in logs or errors
    # Only use it in Authorization header
    self.header = {
      'Authorization': f'Bearer {self.secret_key}',
      'Content-Type': 'application/json',
    }

  def initialize_payment(self, callback_url: str, amount: float, email: str, reference:str,  metadata: Dict[str, str]) -> Dict:
    """Initialize a payment transaction with Paystack"""

    url = f'{self.BASE_URL}/transaction/initialize'
    amount = int(amount * 100)
    data = {
      'amount': amount,
      'email': email,
      'reference': reference
    }

    if callback_url:
      data['callback_url'] = callback_url

    if metadata:
      data['metadata'] = metadata

    try:
      response = requests.post(url, headers=self.header, json=data)
      response.raise_for_status()
      return response.json()
    except requests.exceptions.HTTPError as e:
      # Don't expose secret key in error messages
      error_msg = f"Failed to initialize payment: HTTP {e.response.status_code}"
      if e.response.status_code == 401:
        error_msg += " - Invalid API key (check PAYSTACK_SECRET_KEY)"
      raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
      # Generic error message that doesn't expose sensitive details
      raise Exception(f"Failed to initialize payment: Network error")

  def verify_payment(self, reference: str) -> Dict:
    """Verify a payment transaction with Paystack"""

    url = f'{self.BASE_URL}/transaction/verify/{reference}'
    try:
      response = requests.get(url, headers=self.header)
      response.raise_for_status()
      return response.json()
    except requests.exceptions.HTTPError as e:
      # Don't expose secret key in error messages
      error_msg = f"Failed to verify payment: HTTP {e.response.status_code}"
      if e.response.status_code == 401:
        error_msg += " - Invalid API key (check PAYSTACK_SECRET_KEY)"
      raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
      # Generic error message that doesn't expose sensitive details
      raise Exception(f"Failed to verify payment: Network error")

  def list_transactions(self, page: int = 1, per_page: int = 50) -> Dict:
    """List all payment transactions with Paystack"""

    url = f'{self.BASE_URL}/transaction'
    params = {
      'page': page,
      'per_page': per_page
    }
    try:
      response = requests.get(url, headers=self.header, params=params)
      response.raise_for_status()
      return response.json()
    except requests.exceptions.HTTPError as e:
      # Don't expose secret key in error messages
      error_msg = f"Failed to list transactions: HTTP {e.response.status_code}"
      if e.response.status_code == 401:
        error_msg += " - Invalid API key (check PAYSTACK_SECRET_KEY)"
      raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
      # Generic error message that doesn't expose sensitive details
      raise Exception(f"Failed to list transactions: Network error")