"""URN namespace variants for XAdES signers"""
from .sign_invoice import SignInvoice
from .sign_credit_note import SignCreditNote
from .sign_debit_note import SignDebitNote
from .sign_event import SignEvent

__all__ = ['SignInvoice', 'SignCreditNote', 'SignDebitNote', 'SignEvent']
