import os


def patch_certificate_factory():
    import shoestring.internal.CertificateFactory as certFactoryModule
    originalCertificateFactory = certFactoryModule.CertificateFactory
    originalCertificateFactory._prepare_ca_certificate = _prepare_ca_certificate
    originalCertificateFactory.generate_node_certificate = generate_node_certificate


def _prepare_ca_certificate(self, ca_cn):
    """Prepare CA certificate environment."""

    if not ca_cn:
        raise RuntimeError('CA common name cannot be empty')

    # prepare CA config
    # [CE] Node certificate x509 v3 extension support
    with open('ca.cnf', 'wt', encoding='utf8') as outfile:
        outfile.write('\n'.join([
            '[ca]',
            'default_ca = CA_default',
            '',
            '[CA_default]',
            'new_certs_dir = ./new_certs',
            'database = index.txt',
            'serial = serial.dat',
            f'private_key = {self.ca_key_path}',
            'certificate = ca.crt.pem',
            'policy = policy_catapult',
            '',
            '[policy_catapult]',
            'commonName = supplied',
            '',
            '[req]',
            'prompt = no',
            'distinguished_name = dn',
            'x509_extensions = x509_v3',
            '',
            '[dn]',
            f'CN = {ca_cn}'
            '',
            '[x509_v3]',
            'basicConstraints = critical,CA:TRUE',
            'subjectKeyIdentifier = hash',
            'authorityKeyIdentifier = keyid:always,issuer',
            '',
            '[x509_v3_node]',
            'basicConstraints = CA:FALSE',
            'subjectKeyIdentifier = hash',
            'authorityKeyIdentifier = keyid,issuer'
        ]))

    # create new certs directory
    os.makedirs('new_certs')
    os.chmod('new_certs', 0o700)

    # create index.txt
    with open('index.txt', 'wt', encoding='utf8') as outfile:
        outfile.write('')


def generate_node_certificate(self, node_cn, days=375, start_date=None):
    """Generates a node certificate."""

    if not node_cn:
        raise RuntimeError('Node common name cannot be empty')

    # prepare node config
    # [CE] Node certificate x509 v3 extension support
    with open('node.cnf', 'wt', encoding='utf8') as outfile:
        outfile.write('\n'.join([
            '[req]',
            'prompt = no',
            'distinguished_name = dn',
            '',
            '[dn]',
            f'CN = {node_cn}',
        ]))

    # prepare node certificate signing request
    self.openssl_executor.dispatch([
        'req',
        '-config', 'node.cnf',
        '-key', 'node.key.pem',
        '-new',
        '-out', 'node.csr.pem'
    ])
    self.openssl_executor.dispatch([
        'rand',
        '-out', './serial.dat',
        '-hex',
        '19'
    ])

    # actually generate node certificate
    # [CE] Node certificate x509 v3 extension support
    self.openssl_executor.dispatch(self._add_ca_password([
        'ca',
        '-config', 'ca.cnf',
        '-days', str(days),
        '-notext',
        '-batch',
        '-in', 'node.csr.pem',
        '-out', 'node.crt.pem',
        '-extensions', 'x509_v3_node'
    ] + ([] if not start_date else ['-startdate', start_date.strftime('%y%m%d%H%M%SZ')])))
