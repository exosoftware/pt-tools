{
    "name": "NIF PT",
    "summary": "Implementação das informações dos contactos utilizando o NIF.PT",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "website": "https://exosoftware.pt",
    "author": "Exo Software",
    "maintainers": ["arleite"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "contacts",
        "multi_step_wizard",
        "iap_alternative_provider",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/iap_account_views.xml",
        "wizards/multi_step_wizard_buy_credits_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
