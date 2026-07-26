### Starlab Quality

Modul manajemen mutu ISO 17025 SAI

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch n
bench install-app starlab_quality
```

### Akun

Akun Admin :
Administrator | admin

Akun Testing :
tester@starlab.local | SaiTester2026!

Akun Testing per Role (password sama untuk semua: `Test@12345`) :

- direksi.test@example.com | Direksi
- marketing.test@example.com | Marketing
- administrasi.test@example.com | Administrasi
- finance.test@example.com | Finance
- laboratorium.test@example.com | Laboratorium
- manajerteknis.test@example.com | Manajer Teknis
- manajermutu.test@example.com | Manajer Mutu

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/starlab_quality
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
