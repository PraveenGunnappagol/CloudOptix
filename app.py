# ============================================================================
# PROFESSIONAL CLOUD COST OPTIMIZER - COMPLETE INTEGRATED SOLUTION
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio
import io
import base64
import re
import json
import traceback
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file, make_response
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

app = Flask(__name__)

# ============================================================================
# ADVANCED PROVIDER DETECTION ENGINE (5 Cloud Providers)
# ============================================================================

def detect_provider_from_data(df):
    """
    Advanced provider detection with 90%+ accuracy for 5 providers:
    AWS, Azure, GCP, Oracle Cloud, IBM Cloud
    """
    provider_patterns = {
        'AWS': {
            'compute': ['ec2', 'elastic compute', 'lambda', 'fargate', 'lightsail', 'eks', 'elastic container'],
            'storage': ['s3', 'ebs', 'efs', 'glacier', 'storage gateway', 'amazon s3'],
            'database': ['rds', 'dynamodb', 'aurora', 'redshift', 'elasticache', 'keyspaces'],
            'network': ['vpc', 'cloudfront', 'route53', 'direct connect', 'api gateway'],
            'management': ['cloudwatch', 'cloudtrail', 'config', 'trusted advisor', 'organizations']
        },
        'Azure': {
            'compute': ['virtual machine', 'vm scale', 'app service', 'azure functions', 'aks', 'container instances'],
            'storage': ['blob storage', 'disk storage', 'file storage', 'archive storage', 'azure storage'],
            'database': ['sql database', 'cosmos db', 'database for', 'cache for redis', 'azure sql'],
            'network': ['virtual network', 'load balancer', 'application gateway', 'vpn gateway', 'expressroute'],
            'management': ['azure monitor', 'log analytics', 'advisor', 'cost management', 'policy']
        },
        'GCP': {
            'compute': ['compute engine', 'app engine', 'cloud functions', 'cloud run', 'gke', 'kubernetes engine'],
            'storage': ['cloud storage', 'persistent disk', 'filestore', 'archive storage', 'google storage'],
            'database': ['cloud sql', 'firestore', 'bigtable', 'spanner', 'memorystore', 'datastore'],
            'network': ['vpc network', 'cloud load balancing', 'cloud dns', 'cloud cdn', 'interconnect'],
            'management': ['cloud monitoring', 'cloud logging', 'cloud trace', 'recommender', 'stackdriver']
        },
        'Oracle': {
            'compute': ['oci compute', 'virtual machine', 'bare metal', 'container engine', 'oke', 'functions'],
            'storage': ['object storage', 'block volume', 'file storage', 'archive storage', 'oci storage'],
            'database': ['autonomous database', 'exadata', 'database cloud', 'mysql heatwave', 'oracle database'],
            'network': ['virtual cloud network', 'load balancer', 'vpn', 'fastconnect', 'oci network'],
            'management': ['monitoring service', 'logging service', 'events service', 'oci monitoring']
        },
        'IBM': {
            'compute': ['virtual server', 'bare metal server', 'code engine', 'kubernetes service', 'openshift'],
            'storage': ['cloud object storage', 'block storage', 'file storage', 'cloud storage', 'ibm cos'],
            'database': ['db2 on cloud', 'cloud databases', 'databases for', 'etcd', 'cloudant', 'messages for'],
            'network': ['vpc network', 'load balancer', 'vpn', 'direct link', 'transit gateway'],
            'management': ['activity tracker', 'log analysis', 'monitoring', 'cost management', 'turbonomic']
        }
    }
    
    scores = {provider: 0 for provider in provider_patterns.keys()}
    matches = []
    
    # Analyze all text columns
    text_columns = ['ResourceName', 'Service', 'Department', 'Description']
    for col in text_columns:
        if col in df.columns:
            for value in df[col].dropna().astype(str).str.lower():
                for provider, categories in provider_patterns.items():
                    for category, keywords in categories.items():
                        for keyword in keywords:
                            if keyword in value:
                                scores[provider] += 3
                                matches.append((provider, keyword, col, value[:50]))
                                break
    
    # Also analyze column names
    for col_name in df.columns:
        col_lower = str(col_name).lower()
        for provider, categories in provider_patterns.items():
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in col_lower:
                        scores[provider] += 2
    
    # Determine winner
    total_score = sum(scores.values())
    if total_score > 0:
        best_provider = max(scores, key=scores.get)
        confidence = (scores[best_provider] / total_score) * 100
        
        # Only return if confidence is high
        if confidence >= 50:
            return {
                'provider': best_provider,
                'scores': scores,
                'matches': matches[:10]
            }
    
    return {'provider': 'Unknown', 'scores': scores, 'matches': []}

# ============================================================================
# INSTANCE TYPE KNOWLEDGE BASE (Specific Sizing for All Providers)
# ============================================================================

INSTANCE_KNOWLEDGE_BASE = {'AWS': 
                           {'EC2': {'t3.micro': {'vcpu': 2, 'memory': 1, 'price_hr': 0.0104, 'family': 'General Purpose'},
                 't3.small': {'vcpu': 2, 'memory': 2, 'price_hr': 0.0208, 'family': 'General Purpose'},
                 't3.medium': {'vcpu': 2, 'memory': 4, 'price_hr': 0.0416, 'family': 'General Purpose'},
                 't3.large': {'vcpu': 2, 'memory': 8, 'price_hr': 0.0832, 'family': 'General Purpose'},
                 'm5.large': {'vcpu': 2, 'memory': 8, 'price_hr': 0.096, 'family': 'General Purpose'},
                 'm5.xlarge': {'vcpu': 4, 'memory': 16, 'price_hr': 0.192, 'family': 'General Purpose'},
                 'm5.2xlarge': {'vcpu': 8, 'memory': 32, 'price_hr': 0.384, 'family': 'General Purpose'},
                 'c5.large': {'vcpu': 2, 'memory': 4, 'price_hr': 0.085, 'family': 'Compute Optimized'},
                 'c5.xlarge': {'vcpu': 4, 'memory': 8, 'price_hr': 0.17, 'family': 'Compute Optimized'},
                 'c5.2xlarge': {'vcpu': 8, 'memory': 16, 'price_hr': 0.34, 'family': 'Compute Optimized'},
                 'r5.large': {'vcpu': 2, 'memory': 16, 'price_hr': 0.126, 'family': 'Memory Optimized'},
                 'r5.xlarge': {'vcpu': 4, 'memory': 32, 'price_hr': 0.252, 'family': 'Memory Optimized'},
                 'r5.2xlarge': {'vcpu': 8, 'memory': 64, 'price_hr': 0.504, 'family': 'Memory Optimized'},
                 'i3.large': {'vcpu': 2, 'memory': 15.25, 'price_hr': 0.156, 'family': 'Storage Optimized'},
                 'i3.xlarge': {'vcpu': 4, 'memory': 30.5, 'price_hr': 0.312, 'family': 'Storage Optimized'},
                 'i3.2xlarge': {'vcpu': 8, 'memory': 61, 'price_hr': 0.624, 'family': 'Storage Optimized'}},
         'RDS': {'db.t3.micro': {'vcpu': 2, 'memory': 1, 'price_hr': 0.013, 'family': 'General Purpose'},
                 'db.t3.small': {'vcpu': 2, 'memory': 2, 'price_hr': 0.026},
                 'db.t3.medium': {'vcpu': 2, 'memory': 4, 'price_hr': 0.058},
                 'db.t3.large': {'vcpu': 2, 'memory': 8, 'price_hr': 0.116, 'family': 'General Purpose'},
                 'db.m5.large': {'vcpu': 2, 'memory': 8, 'price_hr': 0.171},
                 'db.m5.xlarge': {'vcpu': 4, 'memory': 16, 'price_hr': 0.342},
                 'db.m5.2xlarge': {'vcpu': 8, 'memory': 32, 'price_hr': 0.684, 'family': 'General Purpose'},
                 'db.r5.large': {'vcpu': 2, 'memory': 16, 'price_hr': 0.24, 'family': 'Memory Optimized'},
                 'db.r5.xlarge': {'vcpu': 4, 'memory': 32, 'price_hr': 0.48, 'family': 'Memory Optimized'},
                 'db.r5.2xlarge': {'vcpu': 8, 'memory': 64, 'price_hr': 0.96, 'family': 'Memory Optimized'}},
         'S3': {'Standard': {'price_hr': 3.150684931506849e-05, 'storage_class': 'Standard'},
                'Standard-IA': {'price_hr': 1.712328767123288e-05, 'storage_class': 'Standard-IA'},
                'Glacier': {'price_hr': 5.479452054794521e-06, 'storage_class': 'Glacier'},
                'Glacier Deep Archive': {'price_hr': 1.3698630136986302e-06, 'storage_class': 'Glacier Deep Archive'}},
         'ElastiCache': {'cache.r5.medium': {'vcpu': 1,
                                             'memory': 6.38,
                                             'price_hr': 0.085,
                                             'family': 'Memory Optimized'},
                         'cache.r5.large': {'vcpu': 2, 'memory': 13.07, 'price_hr': 0.17, 'family': 'Memory Optimized'},
                         'cache.r5.xlarge': {'vcpu': 4,
                                             'memory': 26.32,
                                             'price_hr': 0.34,
                                             'family': 'Memory Optimized'},
                         'cache.r5.2xlarge': {'vcpu': 8,
                                              'memory': 52.82,
                                              'price_hr': 0.68,
                                              'family': 'Memory Optimized'},
                         'cache.t3.micro': {'vcpu': 2, 'memory': 0.5, 'price_hr': 0.017, 'family': 'General Purpose'},
                         'cache.t3.small': {'vcpu': 2, 'memory': 1.37, 'price_hr': 0.034, 'family': 'General Purpose'},
                         'cache.t3.medium': {'vcpu': 2,
                                             'memory': 3.09,
                                             'price_hr': 0.068,
                                             'family': 'General Purpose'}}},
 'Azure': 
 {'Virtual Machine': {'Standard_B1ms': {'vcpu': 1, 'memory': 2, 'price_hr': 0.0104, 'series': 'B-Series'},
                               'Standard_B1s': {'vcpu': 1, 'memory': 1, 'price_hr': 0.0057, 'series': 'B-Series'},
                               'Standard_B2s': {'vcpu': 2, 'memory': 4, 'price_hr': 0.0228, 'series': 'B-Series'},
                               'Standard_B4ms': {'vcpu': 4, 'memory': 16, 'price_hr': 0.0912, 'series': 'B-Series'},
                               'Standard_D2s_v3': {'vcpu': 2, 'memory': 8, 'price_hr': 0.096, 'series': 'D-Series'},
                               'Standard_D4s_v3': {'vcpu': 4, 'memory': 16, 'price_hr': 0.192, 'series': 'D-Series'},
                               'Standard_F2s_v2': {'vcpu': 2, 'memory': 4, 'price_hr': 0.085, 'series': 'F-Series'},
                               'Standard_F4s_v2': {'vcpu': 4, 'memory': 8, 'price_hr': 0.17, 'series': 'F-Series'},
                               'Standard_E2s_v3': {'vcpu': 2, 'memory': 16, 'price_hr': 0.126, 'series': 'E-Series'},
                               'Standard_E4s_v3': {'vcpu': 4, 'memory': 32, 'price_hr': 0.252, 'series': 'E-Series'},
                               'Standard_D8s_v3': {'vcpu': 8, 'memory': 32, 'price_hr': 0.384, 'series': 'D-Series'},
                               'Standard_F8s_v2': {'vcpu': 8, 'memory': 16, 'price_hr': 0.34, 'series': 'F-Series'}},
           'SQL Database': {'Serverless': {'price_hr': 0.003, 'tier': 'Serverless'},
                            'Basic': {'price_hr': 0.0045},
                            'Standard S0': {'price_hr': 0.017},
                            'Standard S1': {'price_hr': 0.034, 'tier': 'Standard'},
                            'Standard S3': {'price_hr': 0.068, 'tier': 'Standard'},
                            'General Purpose GP_Gen5_2': {'price_hr': 0.165},
                            'General Purpose GP_Gen5_4': {'price_hr': 0.33, 'tier': 'General Purpose'},
                            'General Purpose': {'price_hr': 0.25},
                            'BusinessCritical': {'price_hr': 0.42, 'tier': 'Business Critical'}},
           'Blob Storage': {'Hot': {'price_hr': 2.4657534246575342e-05, 'storage_class': 'Hot'},
                            'Cool': {'price_hr': 1.3698630136986302e-05, 'storage_class': 'Cool'},
                            'Archive': {'price_hr': 2.7397260273972604e-06, 'storage_class': 'Archive'},
                            'Archive Deep': {'price_hr': 1.3698630136986302e-06, 'storage_class': 'Archive Deep'}}},
 'GCP': {'Compute Engine': {'e2-micro': {'vcpu': 2, 'memory': 1, 'price_hr': 0.0086, 'family': 'E2'},
                            'e2-small': {'vcpu': 2, 'memory': 2, 'price_hr': 0.0171, 'family': 'E2'},
                            'e2-medium': {'vcpu': 2, 'memory': 4, 'price_hr': 0.0342, 'family': 'E2'},
                            'e2-standard-4': {'vcpu': 4, 'memory': 16, 'price_hr': 0.0684, 'family': 'E2'},
                            'n1-standard-2': {'vcpu': 2, 'memory': 7.5, 'price_hr': 0.095, 'family': 'N1'},
                            'n1-standard-4': {'vcpu': 4, 'memory': 15, 'price_hr': 0.19, 'family': 'N1'},
                            'n1-standard-8': {'vcpu': 8, 'memory': 30, 'price_hr': 0.38, 'family': 'N1'},
                            'n2-standard-2': {'vcpu': 2, 'memory': 8, 'price_hr': 0.0971, 'family': 'N2'},
                            'n2-standard-4': {'vcpu': 4, 'memory': 16, 'price_hr': 0.1942, 'family': 'N2'},
                            'n2-standard-8': {'vcpu': 8, 'memory': 32, 'price_hr': 0.3884, 'family': 'N2'},
                            'c2-standard-4': {'vcpu': 4, 'memory': 16, 'price_hr': 0.208, 'family': 'C2'},
                            'c2-standard-8': {'vcpu': 8, 'memory': 32, 'price_hr': 0.416, 'family': 'C2'},
                            'f1-micro': {'vcpu': 1, 'memory': 0.6, 'price_hr': 0.0076, 'family': 'F1'},
                            'n2d-standard-2': {'vcpu': 2, 'memory': 8, 'price_hr': 0.09, 'family': 'N2D'},
                            'n2d-standard-4': {'vcpu': 4, 'memory': 16, 'price_hr': 0.18, 'family': 'N2D'},
                            'e2-standard-4': {'vcpu': 4,'memory': 16,'price_hr': 0.0684,'family': 'E2'},
                            'Standard': {'vcpu': 2, 'memory': 8, 'price_hr': 0.05, 'family': 'Generic'}},
         'Cloud SQL': {'db-f1-micro': {'price_hr': 0.005},
                       'db-g1-small': {'price_hr': 0.02},
                       'db-n1-standard-2': {'price_hr': 0.092},
                       'db-n1-standard-4': {'price_hr': 0.184},
                       'db-n1-standard-8': {'price_hr': 0.368},
                       'db-custom-4': {'price_hr': 0.15},
                       'db-custom-8': {'price_hr': 0.3},
                       'Shared CPU': {'price_hr': 0.004}},
         'Cloud Storage': {'Standard': {'price_hr': 2.7397260273972603e-05, 'storage_class': 'Standard'},
                           'Nearline': {'price_hr': 1.3698630136986302e-05, 'storage_class': 'Nearline'},
                           'Coldline': {'price_hr': 5.479452054794521e-06, 'storage_class': 'Coldline'},
                           'Archive': {'price_hr': 1.643835616438356e-06, 'storage_class': 'Archive'}}},
 'Oracle': {'Compute': {'VM.GPU3.1': {'vcpu': 4, 'memory': 32, 'price_hr': 1.0, 'family': 'GPU'},
                        'VM.Standard.E2.1': {'vcpu': 1, 'memory': 8, 'price_hr': 0.03, 'family': 'Standard'},
                        'VM.Standard.E2.2': {'vcpu': 2, 'memory': 16, 'price_hr': 0.06, 'family': 'Standard'},
                        'VM.Standard.E2.4': {'vcpu': 4, 'memory': 32, 'price_hr': 0.12, 'family': 'Standard'},
                        'VM.Standard.E3.Flex': {'vcpu': 1, 'memory': 16, 'price_hr': 0.045, 'family': 'Flex'},
                        'VM.Standard.E3.Flex (1 OCPU)': {'vcpu': 1, 'memory': 16, 'price_hr': 0.045, 'family': 'Flex'},
                        'VM.Standard.E3.Flex (2 OCPU)': {'vcpu': 2, 'memory': 32, 'price_hr': 0.09, 'family': 'Flex'},
                        'VM.Standard.E4.Flex': {'vcpu': 4, 'memory': 64, 'price_hr': 0.18, 'family': 'Flex'},
                        'VM.Standard.E4.Flex (4 OCPU)': {'vcpu': 4, 'memory': 64, 'price_hr': 0.18, 'family': 'Flex'},
                        'VM.Standard.E4.Flex (8 OCPU)': {'vcpu': 8, 'memory': 128, 'price_hr': 0.36, 'family': 'Flex'},
                        'VM.Standard.E4.Flex (16 OCPU)': {'vcpu': 16,
                                                          'memory': 256,
                                                          'price_hr': 0.72,
                                                          'family': 'Flex'},
                        'VM.Standard.E4.Flex (32 OCPU)': {'vcpu': 32,
                                                          'memory': 512,
                                                          'price_hr': 1.44,
                                                          'family': 'Flex'},
                        'BM.Standard.E4.128': {'vcpu': 128, 'memory': 2048, 'price_hr': 8.64, 'family': 'Bare Metal'},
                        'VM.DenseIO.E4.128': {'vcpu': 128, 'memory': 2048, 'price_hr': 6.5, 'family': 'DenseIO'},
                        'VM.Standard.E3.Flex (4 OCPU)': {'vcpu': 4, 'memory': 64, 'price_hr': 0.18, 'family': 'Flex'},
                        'VM.Standard.E2.8': {'vcpu': 8, 'memory': 64, 'price_hr': 0.24, 'family': 'Standard'}},
            'Autonomous Database': {'0.5 OCPU': {'price_hr': 0.15},
                                    '1 OCPU': {'price_hr': 0.3},
                                    '2 OCPU': {'price_hr': 0.6},
                                    '4 OCPU': {'price_hr': 1.2},
                                    '8 OCPU': {'price_hr': 2.4}}},
 'IBM': {'Virtual Server': {'bx2.2x8': {'vcpu': 2, 'memory': 8, 'price_hr': 0.096, 'family': 'Balanced'},
                            'bx2.4x16': {'vcpu': 4, 'memory': 16, 'price_hr': 0.192, 'family': 'Balanced'},
                            'bx2.8x32': {'vcpu': 8, 'memory': 32, 'price_hr': 0.384, 'family': 'Balanced'},
                            'bx2.16x64': {'vcpu': 16, 'memory': 64, 'price_hr': 0.768, 'family': 'Balanced'},
                            'cx2.4x8': {'vcpu': 4, 'memory': 8, 'price_hr': 0.17, 'family': 'Compute'},
                            'cx2.8x16': {'vcpu': 8, 'memory': 16, 'price_hr': 0.34, 'family': 'Compute'},
                            'mx2.4x32': {'vcpu': 4, 'memory': 32, 'price_hr': 0.32, 'family': 'Memory'},
                            'mx2.8x64': {'vcpu': 8, 'memory': 64, 'price_hr': 0.64, 'family': 'Memory'},
                            'mx2.16x128': {'vcpu': 16, 'memory': 128, 'price_hr': 1.28, 'family': 'Memory'},
                            'vx2.2x8': {'vcpu': 2, 'memory': 8, 'price_hr': 0.11, 'family': 'Very High Memory'},
                            'vx2.4x16': {'vcpu': 4, 'memory': 16, 'price_hr': 0.22, 'family': 'Very High Memory'},
                            'cx2.2x4': {'vcpu': 2, 'memory': 4, 'price_hr': 0.085, 'family': 'Compute'},
                            'mx2.2x16': {'vcpu': 2, 'memory': 16, 'price_hr': 0.16, 'family': 'Memory'}},
         'Cloud Object Storage': {'Standard': {'price_hr': 0.0025},
                                  'Vault': {'price_hr': 0.0015},
                                  'Cold Vault': {'price_hr': 0.0009},
                                  'Archive': {'price_hr': 0.0005, 'storage_class': 'Archive'}
                                  }}}


# ============================================================================
# INSTANCE TYPE DETECTION FROM RESOURCE NAMES
# ============================================================================

def detect_instance_type(resource_name, provider='AWS'):
    """
    Detect specific instance types from resource names (AWS, Azure, GCP, Oracle, IBM)
    """
    if pd.isna(resource_name):
        return 'Unknown'
    
    resource_lower = str(resource_name).lower()

    # ============================
    # AWS INSTANCE TYPE PATTERNS
    # ============================
    aws_patterns = [
        # EC2 common
        (r'\b([a-z]\d+[a-z]*\.(?:nano|micro|small|medium|large|xlarge|2xlarge|4xlarge|8xlarge|12xlarge|16xlarge|24xlarge|32xlarge|metal))\b', 'EC2'),
        # RDS
        (r'\b(db\.[a-z]\d+[a-z]*\.(?:micro|small|medium|large|xlarge|2xlarge|4xlarge))\b', 'RDS'),
    ]

    # ============================
    # AZURE INSTANCE TYPE PATTERNS
    # ============================
    azure_patterns = [
    (r'\b(Standard_[A-Z]\d+[a-z]*_v\d+)\b', 'Virtual Machine'),
    (r'\b(Standard_[A-Z]\d+[a-z]*)\b', 'Virtual Machine'),
    (r'\b(Basic_[A-Z]\d+)\b', 'Virtual Machine'),
    (r'\b(Standard_B\d+[a-z]*)\b', 'Virtual Machine'),
    (r'\b(Standard_F\d+[a-z]*_v\d+)\b', 'Virtual Machine'),  # ADDED
    (r'\b(Standard_E\d+[a-z]*_v\d+)\b', 'Virtual Machine'),  # ADDED
    (r'\b(Standard_D\d+[a-z]*_v\d+)\b', 'Virtual Machine'),  # ADDED
    (r'\b(Standard_[A-Z]\d+[a-z]*_v\d+_Promo)\b', 'Virtual Machine'),  # ADDED
    (r'\b(DC\d+s_v\d+)\b', 'Virtual Machine'),
]

    # ============================
    # GCP INSTANCE TYPE PATTERNS
    # ============================
    gcp_patterns = [
    (r'\b(n1-(?:standard|highcpu|highmem)-\d+)\b', 'Compute Engine'),
    (r'\b(n2-(?:standard|highcpu|highmem)-\d+)\b', 'Compute Engine'),
    (r'\b(n2d-(?:standard|highcpu|highmem)-\d+)\b', 'Compute Engine'),
    (r'\b(e2-(?:micro|small|medium|standard-\d+|highcpu-\d+|highmem-\d+))\b', 'Compute Engine'),
    (r'\b(c2-(?:standard|highcpu)-\d+)\b', 'Compute Engine'),
    (r'\b(c3-(?:standard|highcpu|highmem)-\d+)\b', 'Compute Engine'),
    (r'\b(t2d-(?:standard)-\d+)\b', 'Compute Engine'),
    (r'\b(m1-ultramem-\d+)\b', 'Compute Engine'),
    (r'\b(m2-ultramem-\d+)\b', 'Compute Engine'),
    (r'\b(m3-ultramem-\d+)\b', 'Compute Engine'),
    (r'\b(db-[a-z]+-\d+)\b', 'Cloud SQL'),
    (r'\b(db-custom-\d+-\d+)\b', 'Cloud SQL'),  # ADDED
    (r'\b(db-n1-\w+-\d+)\b', 'Cloud SQL'),  # ADDED
]

    # ============================
    # ORACLE INSTANCE TYPE PATTERNS
    # ============================
    oracle_patterns = [
        (r'\b(VM\.Standard\.E\d+\.Flex)\b', 'Compute'),
        (r'\b(VM\.Standard\.E\d+\.\d+)\b', 'Compute'),
        (r'\b(VM\.Standard\.\w+\.\d+)\b', 'Compute'),
        (r'\b(BM\.Standard\.\w+\.\d+)\b', 'Compute'),
        (r'\b(VM\.GPU\d+\.\d+)\b', 'Compute'),
        (r'\b(VM\.DenseIO\.\w+\.\d+)\b', 'Compute'),
        (r'\b(VM\.Optimized\.\w+\.\d+)\b', 'Compute'),
        (r'\b(\d+\s*OCPU)\b', 'Autonomous Database'),
        (r'\b(OLTP|DW|APEX)\b', 'Autonomous Database'),
    ]
    # ============================
    # IBM INSTANCE TYPE PATTERNS
    # ============================
        # ============================
    # IBM INSTANCE TYPE PATTERNS
    # ============================
    ibm_patterns = [
        (r'\b(bx\d+\.\d+x\d+)\b', 'Virtual Server'),
        (r'\b(cx\d+\.\d+x\d+)\b', 'Virtual Server'),
        (r'\b(mx\d+\.\d+x\d+)\b', 'Virtual Server'),
        (r'\b(vx\d+\.\d+x\d+)\b', 'Virtual Server'),
        (r'\b(bl\d+\.\d+x\d+)\b', 'Virtual Server'),
        (r'\b(\d+vcpu-\d+gb)\b', 'Virtual Server'),
        (r'\b(\d+x\d+)\b', 'Virtual Server'),
        (r'\b(Standard|Vault|Cold Vault|Archive|Flex)\b', 'Cloud Object Storage'),
    ]

    # Map provider → patterns
    patterns_map = {
        'AWS': aws_patterns,
        'Azure': azure_patterns,
        'GCP': gcp_patterns,
        'Oracle': oracle_patterns,
        'IBM': ibm_patterns
    }

    # ============================
    # MATCH SPECIFIC PROVIDER PATTERNS
    # ============================
    if provider in patterns_map:
        for pattern, service_type in patterns_map[provider]:
            match = re.search(pattern, resource_lower)
            if match:
                return match.group(1)

    # ============================
    # GENERIC INSTANCE KEYWORD FALLBACK
    # ============================
    generic_patterns = [
        (r'\b(\d+vcpu)\b', 'Generic'),
        (r'\b(\d+\s*cpu)\b', 'Generic'),
        (r'\b(\d+\s*gb)\b', 'Generic'),
        (r'\b(standard-\d+)\b', 'Generic'),
        (r'\b(highcpu-\d+)\b', 'Generic'),
        (r'\b(highmem-\d+)\b', 'Generic'),
        (r'\b(micro|small|medium|large|xlarge|2xlarge)\b', 'Generic'),
    ]

    for pattern, service_type in generic_patterns:
        match = re.search(pattern, resource_lower)
        if match:
            return match.group(1)

    return 'Unknown'

# ============================================================================
# ADVANCED DATA VALIDATION AND QUALITY SCORING
# ============================================================================

def validate_and_score_data(df):
    """
    Comprehensive data validation with quality scoring (0-100)
    """
    warnings = []
    cleaned_df = df.copy()
    score = 100
    
    # 1. Check required columns
    required_cols = ['Cost']
    missing_required = [col for col in required_cols if col not in df.columns]
    if missing_required:
        warnings.append({
            'level': 'high',
            'message': f'Missing required column: {", ".join(missing_required)}',
            'suggestion': 'Add a cost column with numeric values'
        })
        score -= 30
    
    # 2. Normalize column names
    column_mapping = {}
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if 'cost' in col_lower or 'amount' in col_lower or 'usd' in col_lower or 'price' in col_lower:
            column_mapping[col] = 'Cost'
        elif 'resource' in col_lower or 'name' in col_lower or 'id' in col_lower or 'instance' in col_lower:
            column_mapping[col] = 'ResourceName'
        elif 'service' in col_lower or 'type' in col_lower or 'product' in col_lower:
            column_mapping[col] = 'Service'
        elif 'util' in col_lower or 'usage' in col_lower or 'cpu' in col_lower or 'percent' in col_lower:
            column_mapping[col] = 'Utilization'
        elif 'department' in col_lower or 'team' in col_lower or 'project' in col_lower:
            column_mapping[col] = 'Department'
        elif 'date' in col_lower or 'month' in col_lower or 'period' in col_lower:
            column_mapping[col] = 'Date'
    
    cleaned_df = cleaned_df.rename(columns={k: v for k, v in column_mapping.items() if v not in cleaned_df.columns})
    
    # 3. Validate Cost column
    if 'Cost' in cleaned_df.columns:
        original_non_null = cleaned_df['Cost'].count()
        cleaned_df['Cost'] = pd.to_numeric(cleaned_df['Cost'], errors='coerce')
        after_conversion = cleaned_df['Cost'].count()
        
        if after_conversion < original_non_null:
            warnings.append({
                'level': 'medium',
                'message': f'Fixed {original_non_null - after_conversion} non-numeric cost values',
                'suggestion': 'Ensure cost values are numbers (no currency symbols)'
            })
            score -= 10
        
        # Check for negative costs (might be credits)
        negative_costs = (cleaned_df['Cost'] < 0).sum()
        if negative_costs > 0:
            warnings.append({
                'level': 'low',
                'message': f'Found {negative_costs} negative costs (might be credits)',
                'suggestion': 'Review if these are actual credits or data errors'
            })
        
        # Fill NaN with 0
        nan_count = cleaned_df['Cost'].isna().sum()
        if nan_count > 0:
            cleaned_df['Cost'] = cleaned_df['Cost'].fillna(0)
            warnings.append({
                'level': 'medium',
                'message': f'Filled {nan_count} missing cost values with 0',
                'suggestion': 'Provide actual cost values for better analysis'
            })
            score -= 5
    
    # 4. Validate Utilization column
    if 'Utilization' in cleaned_df.columns:
        cleaned_df['Utilization'] = pd.to_numeric(cleaned_df['Utilization'], errors='coerce')
        # Clip to 0-100 range
        cleaned_df['Utilization'] = cleaned_df['Utilization'].clip(0, 100)
        
        # Check for values outside range
        out_of_range = ((cleaned_df['Utilization'] < 0) | (cleaned_df['Utilization'] > 100)).sum()
        if out_of_range > 0:
            warnings.append({
                'level': 'low',
                'message': f'Fixed {out_of_range} utilization values outside 0-100% range',
                'suggestion': 'Utilization should be between 0 and 100%'
            })
        
        # Fill missing with median or 50
        missing_util = cleaned_df['Utilization'].isna().sum()
        if missing_util > 0:
            median_util = cleaned_df['Utilization'].median()
            if pd.isna(median_util):
                median_util = 50
            cleaned_df['Utilization'] = cleaned_df['Utilization'].fillna(median_util)
            warnings.append({
                'level': 'low',
                'message': f'Estimated {missing_util} missing utilization values as {median_util:.1f}%',
                'suggestion': 'Add actual utilization metrics for accurate analysis'
            })
    
    # 5. Ensure ResourceName exists
    if 'ResourceName' not in cleaned_df.columns:
        cleaned_df['ResourceName'] = [f'Resource_{i+1:04d}' for i in range(len(cleaned_df))]
        warnings.append({
            'level': 'medium',
            'message': 'No resource names found - generated generic names',
            'suggestion': 'Add a ResourceName column for better tracking'
        })
        score -= 10
    
    # 6. Ensure Service column exists
    if 'Service' not in cleaned_df.columns:
        cleaned_df['Service'] = 'Unknown Service'
        warnings.append({
            'level': 'medium',
            'message': 'No service types specified',
            'suggestion': 'Add service names (EC2, VM, Compute Engine, etc.) for provider detection'
        })
        score -= 15
    
    # 7. Ensure Department column exists
    if 'Department' not in cleaned_df.columns:
        cleaned_df['Department'] = 'Unassigned'
        warnings.append({
            'level': 'low',
            'message': 'No department/team information',
            'suggestion': 'Add department for cost allocation'
        })
        score -= 5
    
    # Calculate final score (0-100)
    score = max(0, min(100, score))
    
    return {
        'cleaned_df': cleaned_df,
        'warnings': warnings,
        'quality_score': score,
        'total_rows': len(cleaned_df),
        'valid_rows': len(cleaned_df[cleaned_df['Cost'] > 0])
    }

# ============================================================================
# GENERATE SPECIFIC RECOMMENDATIONS FOR ALL PROVIDERS
# ============================================================================

def generate_specific_recommendations(df, provider, analysis_summary):
    """
    Unified function to generate SPECIFIC, actionable recommendations for all cloud providers
    including compute, database, and storage resources.
    """
    recommendations = []
    total_monthly_cost = analysis_summary.get('total_cost', 0)

    # Downgrade map
    downgrade_map = {

    # ========================================================================
    # AWS
    # ========================================================================
    'AWS': {

        # --------------------------------------------------------------------
        # EC2
        # --------------------------------------------------------------------
        'EC2': {
            'm5.2xlarge': 'm5.xlarge',
            'm5.xlarge': 'm5.large',
            'm5.large': 't3.large',
            't3.large': 't3.medium',
            't3.medium': 't3.small',

            'c5.2xlarge': 'c5.xlarge',
            'c5.xlarge': 'c5.large',
            'c5.large': 't3.medium',

            'r5.2xlarge': 'r5.xlarge',
            'r5.xlarge': 'r5.large',
            'r5.large': 't3.large',

            'i3.2xlarge': 'i3.xlarge',
            'i3.xlarge': 'i3.large'
        },

        # --------------------------------------------------------------------
        # RDS
        # --------------------------------------------------------------------
        'RDS': {
            'db.m5.2xlarge': 'db.m5.xlarge',
            'db.m5.xlarge': 'db.m5.large',
            'db.m5.large': 'db.t3.medium',

            'db.t3.large': 'db.t3.medium',
            'db.t3.medium': 'db.t3.small',

            'db.r5.2xlarge': 'db.r5.xlarge',
            'db.r5.xlarge': 'db.r5.large'
        },

        # --------------------------------------------------------------------
        # S3
        # --------------------------------------------------------------------
        'S3': {
            'Standard': 'Standard-IA',
            'Standard-IA': 'Glacier',
            'Glacier': 'Glacier Deep Archive'
        },

        # --------------------------------------------------------------------
        # ElastiCache
        # --------------------------------------------------------------------
        'ElastiCache': {
            'cache.r5.2xlarge': 'cache.r5.xlarge',
            'cache.r5.xlarge': 'cache.r5.large',
            'cache.r5.large': 'cache.r5.medium',

            'cache.t3.medium': 'cache.t3.small',
            'cache.t3.small': 'cache.t3.micro'
        }
    },


    # ========================================================================
    # AZURE
    # ========================================================================
    'Azure': {

        # --------------------------------------------------------------------
        # Virtual Machine
        # --------------------------------------------------------------------
        'Virtual Machine': {
            'Standard_D4s_v3': 'Standard_D2s_v3',
            'Standard_D2s_v3': 'Standard_B2s',
            'Standard_B2s': 'Standard_B1s',
            'Standard_B1s': 'Standard_B1ms',

            'Standard_F4s_v2': 'Standard_F2s_v2',
            'Standard_F2s_v2': 'Standard_B1s',

            'Standard_E4s_v3': 'Standard_E2s_v3',
            'Standard_E2s_v3': 'Standard_B2s',

            'Standard_B4ms': 'Standard_B2s',

            'Standard_D8s_v3': 'Standard_D4s_v3',
            'Standard_F8s_v2': 'Standard_F4s_v2'
        },

        # --------------------------------------------------------------------
        # SQL Database
        # --------------------------------------------------------------------
        'SQL Database': {
            'BusinessCritical': 'General Purpose GP_Gen5_4',

            'General Purpose GP_Gen5_4': 'General Purpose GP_Gen5_2',
            'General Purpose GP_Gen5_2': 'Basic',

            'Standard S3': 'Standard S1',
            'Standard S1': 'Basic',

            'Standard S0': 'Basic'
        },

        # --------------------------------------------------------------------
        # Blob Storage
        # --------------------------------------------------------------------
        'Blob Storage': {
            'Hot': 'Cool',
            'Cool': 'Archive',
            'Archive': 'Archive Deep'
        },

        # --------------------------------------------------------------------
        # Redis Cache
        # --------------------------------------------------------------------
        'Redis Cache': {
            'Premium': 'Standard',
            'Standard': 'Basic'
        },

        # --------------------------------------------------------------------
        # App Service
        # --------------------------------------------------------------------
        'App Service': {
            'S1': 'B2',
            'B2': 'B1'
        },

        # --------------------------------------------------------------------
        # VPN Gateway
        # --------------------------------------------------------------------
        'VPN Gateway': {
            'VpnGw1': 'Basic'
        },

        # --------------------------------------------------------------------
        # AKS Cluster
        # --------------------------------------------------------------------
        'AKS Cluster': {
            'Standard': 'Basic'
        },

        # --------------------------------------------------------------------
        # CDN
        # --------------------------------------------------------------------
        'CDN': {
            'Premium': 'Standard'
        }
    },


    # ========================================================================
    # GCP
    # ========================================================================
    'GCP': {

        # --------------------------------------------------------------------
        # Compute Engine
        # --------------------------------------------------------------------
        'Compute Engine': {
            'n2-standard-8': 'n2-standard-4',
            'n2-standard-4': 'n2-standard-2',
            'n2-standard-2': 'e2-medium',

            'e2-medium': 'e2-small',
            'e2-small': 'e2-micro',

            'c2-standard-8': 'c2-standard-4',
            'c2-standard-4': 'n2-standard-2',

            'n1-standard-8': 'n1-standard-4',
            'n1-standard-4': 'n1-standard-2',

            # Changed from f1-micro because f1-micro is
            # not present in the Compute Engine knowledge base.
            'n1-standard-2': 'e2-medium',

            'n2d-standard-4': 'n2d-standard-2',
            'e2-standard-4': 'e2-medium'
        },

        # --------------------------------------------------------------------
        # Cloud SQL
        # --------------------------------------------------------------------
        'Cloud SQL': {
            'db-n1-standard-8': 'db-n1-standard-4',
            'db-n1-standard-4': 'db-n1-standard-2',
            'db-n1-standard-2': 'db-g1-small',

            'db-g1-small': 'db-f1-micro',

            'db-custom-8': 'db-custom-4'
        },

        # --------------------------------------------------------------------
        # Cloud Storage
        # --------------------------------------------------------------------
        'Cloud Storage': {
            'Standard': 'Nearline',
            'Nearline': 'Coldline',
            'Coldline': 'Archive'
        },

        # --------------------------------------------------------------------
        # GKE Cluster
        # --------------------------------------------------------------------
        'GKE Cluster': {
            'Standard': 'Basic'
        },

        # --------------------------------------------------------------------
        # Memorystore
        # --------------------------------------------------------------------
        'Memorystore': {
            'Premium': 'Standard',
            'Standard': 'Basic'
        },

        # --------------------------------------------------------------------
        # App Engine
        # --------------------------------------------------------------------
        'App Engine': {
            'F4': 'F2',
            'F2': 'F1'
        },

        # --------------------------------------------------------------------
        # Cloud VPN
        # --------------------------------------------------------------------
        'Cloud VPN': {
            'Standard': 'Basic'
        },

        # --------------------------------------------------------------------
        # Cloud CDN
        # --------------------------------------------------------------------
        'Cloud CDN': {
            'Premium': 'Standard'
        }
    },


    # ========================================================================
    # ORACLE
    # ========================================================================
    'Oracle': {

        # --------------------------------------------------------------------
        # Compute
        # --------------------------------------------------------------------
        'Compute': {

            'VM.GPU3.1': 'VM.Standard.E4.Flex',

            'VM.Standard.E4.Flex': 'VM.Standard.E3.Flex',

            # IMPORTANT:
            # canonicalize_instance_type() removes "(2 OCPU)"
            # and "(1 OCPU)", therefore the map key must be:
            # VM.Standard.E3.Flex
            #
            # E3 Flex = $0.090/hr
            # E2.2    = $0.060/hr
            #
            # This now produces genuine savings.
            'VM.Standard.E3.Flex': 'VM.Standard.E2.2',

            'VM.Standard.E2.4': 'VM.Standard.E2.2',
            'VM.Standard.E2.2': 'VM.Standard.E2.1',

            'BM.Standard.E4.128': 'VM.Standard.E4.Flex',
            'VM.DenseIO.E4.128': 'VM.Standard.E4.Flex'
        },

        # --------------------------------------------------------------------
        # Autonomous Database
        # --------------------------------------------------------------------
        'Autonomous Database': {
            '8 OCPU': '4 OCPU',
            '4 OCPU': '2 OCPU',
            '2 OCPU': '1 OCPU',
            '1 OCPU': '0.5 OCPU'
        }
    },


    # ========================================================================
    # IBM
    # ========================================================================
    'IBM': {

        # --------------------------------------------------------------------
        # Virtual Server
        # --------------------------------------------------------------------
        'Virtual Server': {
            'mx2.16x128': 'mx2.8x64',
            'mx2.8x64': 'mx2.4x32',
            'mx2.4x32': 'bx2.4x16',

            'bx2.16x64': 'bx2.8x32',
            'bx2.8x32': 'bx2.4x16',
            'bx2.4x16': 'cx2.4x8',

            'cx2.8x16': 'cx2.4x8',
            'cx2.4x8': 'bx2.2x8',

            'vx2.4x16': 'vx2.2x8',

            'mx2.2x16': 'bx2.2x8'
        },

        # --------------------------------------------------------------------
        # Cloud Object Storage
        # --------------------------------------------------------------------
        'Cloud Object Storage': {
            'Standard': 'Vault',
            'Vault': 'Cold Vault',
            'Cold Vault': 'Archive'
        }
    }
}

    # list of services to scan
    compute_services = ['EC2', 'RDS', 'S3', 'Virtual Machine', 'SQL Database', 'Blob Storage',
                        'Compute Engine', 'Cloud SQL', 'Cloud Storage', 'Compute', 'Autonomous Database',
                        'Virtual Server', 'Cloud Object Storage']

    # Include every service present in the uploaded data so recommendations are
    # generated for ALL underutilized services, not only the predefined list.
    if 'Service' in df.columns:
        # Deduplicate case-insensitively so values such as "EC2" and "ec2"
        # cannot cause the same resource to receive duplicate recommendations.
        services_seen = {str(service).strip().lower() for service in compute_services}
        for service in df['Service'].dropna().astype(str).str.strip():
            service_key = service.lower()
            if service_key not in services_seen:
                compute_services.append(service)
                services_seen.add(service_key)

    # SERVICE normalization map
    # Update this dictionary to include the exact service names from your data
    SERVICE_NORMALIZATION_MAP = {
        # AWS
        "ec2": "EC2",
        "rds": "RDS",
        "s3": "S3",
        "elastic compute": "EC2",
        "elastic container": "EC2",
    
    # Azure (from your data)
    "virtual machine": "Virtual Machine",
    "vm": "Virtual Machine",
    "sql database": "SQL Database",
    "blob storage": "Blob Storage",
    "azure vm": "Virtual Machine",
    "redis cache": "Redis Cache",  # ADDED
    "app service": "App Service",  # ADDED
    "vpn gateway": "VPN Gateway",  # ADDED
    "aks cluster": "AKS Cluster",  # ADDED
    "cdn": "CDN",  # ADDED
    
    # GCP (from your data)
    "compute engine": "Compute Engine",
    "cloud sql": "Cloud SQL",
    "cloud storage": "Cloud Storage",
    "gke cluster": "GKE Cluster",
    "google kubernetes": "GKE Cluster",
    "memorystore": "Memorystore",  # ADDED
    "app engine": "App Engine",  # ADDED
    "cloud vpn": "Cloud VPN",  # ADDED
    "cloud cdn": "Cloud CDN",  # ADDED
    
    # Oracle
    "compute": "Compute",
    "oci compute": "Compute",
    "virtual machine": "Compute",
    "vm": "Compute",
    "autonomous database": "Autonomous Database",
    "autonomous db": "Autonomous Database",
    "adb": "Autonomous Database",
    "oci database": "Autonomous Database",
    
    # IBM
    "virtual server": "Virtual Server",
    "cloud virtual server": "Virtual Server",
    "ibm virtual server": "Virtual Server",
    "cloud object storage": "Cloud Object Storage",
    "object storage": "Cloud Object Storage",
    "ibm kubernetes": "GKE Cluster",
    "code engine": "App Engine",
    "database for redis": "Memorystore",
    "transit gateway": "Cloud VPN",
    "file storage": "Cloud Storage",
    "cloud dns": "Cloud DNS",
}

    def apply_fallback_heuristics(instance_type, service, provider):
        """
        Apply intelligent fallback heuristics when no direct downgrade mapping is found
        """
        if not instance_type or instance_type == 'Unknown':
            return f"Smaller {service}"
            
        lower = instance_type.lower()
        
        # Provider-specific heuristics
        if provider == 'Azure':
            if 'standard_d' in lower:
                if 'd4' in lower:
                    return 'Standard_D2s_v3'
                elif 'd2' in lower:
                    return 'Standard_B2s'
                elif 'b2' in lower:
                    return 'Standard_B1s'
            elif 'standard_f' in lower:
                if 'f4' in lower:
                    return 'Standard_F2s_v2'
                elif 'f2' in lower:
                    return 'Standard_B1s'
            elif 'standard_e' in lower:
                if 'e4' in lower:
                    return 'Standard_E2s_v3'
                elif 'e2' in lower:
                    return 'Standard_B2s'
            elif 'standard_b' in lower:
                if 'b4' in lower:
                    return 'Standard_B2s'
                elif 'b2' in lower:
                    return 'Standard_B1s'
            return 'Standard_B1s'
        
        
        
        elif provider == 'IBM':
            if '16x' in lower:
                parts = instance_type.split('.')
                if len(parts) == 2:
                    size_part = parts[1]
                    if '16x' in size_part:
                        return size_part.replace('16x', '8x')
            elif '8x' in lower:
                parts = instance_type.split('.')
                if len(parts) == 2:
                    size_part = parts[1]
                    if '8x' in size_part:
                        return size_part.replace('8x', '4x')
            elif '4x' in lower:
                if instance_type.startswith('cx2'):
                    return 'bx2.4x16'
            return f"Smaller {service}"
        
        elif provider == 'Oracle':
            if 'gpu' in lower:
                return 'VM.Standard.E4.Flex'
            elif '128' in lower:
                return '64 OCPU'
            elif '64' in lower:
                return '32 OCPU'
            elif '32' in lower:
                return '16 OCPU'
            elif 'flex' in lower:
                return 'VM.Standard.E3.Flex'
            elif 'e4' in lower:
                return 'VM.Standard.E3.Flex'
            elif 'e3' in lower:
                return 'VM.Standard.E2.4'
            elif 'e2.4' in lower:
                return 'VM.Standard.E2.2'
            elif 'e2.2' in lower:
                return 'VM.Standard.E2.1'
            return f"Smaller {service}"
        
        # General heuristics for all providers
        if 'xlarge' in lower:
            return instance_type.replace('xlarge', 'large')
        elif 'large' in lower:
            return instance_type.replace('large', 'medium')
        elif 'medium' in lower:
            return instance_type.replace('medium', 'small')
        elif 'hot' in lower:
            return 'Cool'
        elif 'cool' in lower:
            return 'Archive'
        elif 'archive' in lower:
            return 'Archive Deep'
        elif 'basic' in lower:
            return 'General Purpose'
        elif 'standard' in lower and 'premium' not in lower:
            return 'Basic'
        elif 'enterprise' in lower:
            return 'Standard'
        
        # Default fallback
        return f"Smaller {service}"

    # Instance type canonicalization helper
        # Instance type canonicalization helper
    def canonicalize_instance_type(raw):
        """
        Clean and canonicalize raw instance type string so it matches keys in downgrade_map.
        """
        if not raw or raw is None:
            return 'Unknown'
        
        s = str(raw).strip()
        
        # Remove parentheses with contents but keep OCPU info for Oracle
        s = re.sub(r'\s*\([^)]*\)', '', s)
        
        # Handle Oracle Flex instances
        if 'Flex' in s and 'OCPU' not in s:
            # Try to extract OCPU count from context
            s = s.strip()
        
        # Handle IBM patterns
        if provider == 'IBM':
            # Normalize IBM patterns like "bx2.4x16" 
            s = s.lower().strip()
            # Ensure proper format
            if re.match(r'^[a-z]+\d+\.\d+x\d+$', s):
                return s
        
        # Handle Oracle patterns  
        if provider == 'Oracle':
            # Extract just the instance type part
            if 'VM.' in s or 'BM.' in s:
                # Keep the VM.Standard.E4.Flex format
                s = re.sub(r'\s+', '', s)
                return s
            elif 'OCPU' in s:
                # For Autonomous Database
                return s.strip()
        
        # Azure formatting
        m_azure = re.match(r'^(standard)\s*[-_ ]?([A-Za-z0-9]+)\s*[_\s]?v?(\d+)$', s, flags=re.I)
        if m_azure:
            return f"Standard_{m_azure.group(2)}_v{m_azure.group(3)}"
        
        # Return cleaned string
        return s.strip()

    for compute_service in compute_services:
        compute_resources = df[df['Service'].str.strip().str.lower() == compute_service.strip().lower()]

        if 'Utilization' not in compute_resources.columns or 'Cost' not in compute_resources.columns:
            continue

        underutilized = compute_resources[compute_resources['Utilization'] < 40]

        for _, resource in underutilized.iterrows():
            # Service normalization
            raw_service = str(resource.get('Service', '')).strip().lower()
            service_key = SERVICE_NORMALIZATION_MAP.get(raw_service, None)
            if not service_key:
                if compute_service.lower() in raw_service:
                    service_key = compute_service
                else:
                    continue
            compute_service_normalized = service_key

            # Get instance type
            raw_instance = None
            for candidate in ['InstanceType', 'MachineType', 'Machine Type', 'instance', 'machine']:
                if candidate in resource:
                    raw_instance = resource.get(candidate)
                    if pd.notna(raw_instance) and str(raw_instance).strip() != '':
                        break
                    else:
                        raw_instance = None

            if not raw_instance or str(raw_instance).strip().lower() in ['none', 'nan', 'unknown', '']:
                resource_name = resource.get('ResourceName', '')
                detected = detect_instance_type(resource_name, provider) if resource_name else 'Unknown'
                raw_instance = detected if detected and detected != 'Unknown' else None

            instance_type = canonicalize_instance_type(raw_instance) if raw_instance else 'Unknown'
            cost = float(resource.get('Cost', 0))
            util = float(resource.get('Utilization', 0))
            resource_name = resource.get('ResourceName', 'Unknown')

            # Do not impose a minimum-cost cutoff. Every resource/service with
            # utilization below 40% should receive a recommendation.
            recommended = instance_type

            # Lookup specific downgrade
                        # Lookup specific downgrade using the canonical instance_type and service key
            if provider in downgrade_map:
                # First try exact service key match
                if compute_service_normalized in downgrade_map[provider]:
                    # Try direct lookup first
                    if instance_type in downgrade_map[provider][compute_service_normalized]:
                        recommended = downgrade_map[provider][compute_service_normalized][instance_type]
                    else:
                        # Try case-insensitive lookup
                        for map_key, map_val in downgrade_map[provider][compute_service_normalized].items():
                            if map_key.lower() == instance_type.lower():
                                recommended = map_val
                                break
                        else:
                            # Try partial match (e.g., "VM.Standard.E4.Flex" when key is "VM.Standard.E4.Flex (4 OCPU)")
                            for map_key, map_val in downgrade_map[provider][compute_service_normalized].items():
                                if instance_type in map_key or map_key in instance_type:
                                    recommended = map_val
                                    break
                            else:
                                # Fallback heuristics
                                recommended = apply_fallback_heuristics(instance_type, compute_service_normalized, provider)
                else:
                    # Try to find matching service
                    found_service = False
                    for svc_key in downgrade_map[provider]:
                        if compute_service_normalized.lower() in svc_key.lower() or svc_key.lower() in compute_service_normalized.lower():
                            found_service = True
                            # Try direct lookup first
                            if instance_type in downgrade_map[provider][svc_key]:
                                recommended = downgrade_map[provider][svc_key][instance_type]
                                break
                            else:
                                # Try case-insensitive lookup
                                for map_key, map_val in downgrade_map[provider][svc_key].items():
                                    if map_key.lower() == instance_type.lower():
                                        recommended = map_val
                                        break
                                else:
                                    # Try partial match
                                    for map_key, map_val in downgrade_map[provider][svc_key].items():
                                        if instance_type in map_key or map_key in instance_type:
                                            recommended = map_val
                                            break
                                    else:
                                        # Fallback heuristics
                                        recommended = apply_fallback_heuristics(instance_type, compute_service_normalized, provider)
                                break
                    
                    if not found_service:
                        # No matching service found, use fallback
                        recommended = apply_fallback_heuristics(instance_type, compute_service_normalized, provider)
            else:
                # Provider not in downgrade map
                recommended = apply_fallback_heuristics(instance_type, compute_service_normalized, provider)

                # ============================================================
            # CALCULATE POTENTIAL SAVINGS FROM INSTANCE PRICE DIFFERENCE
            # ============================================================

            current_price_hr = None
            recommended_price_hr = None

            # Search for the current and recommended instance prices
            # across all services for the detected provider.
            # This avoids problems when the service name in the uploaded
            # data does not exactly match the knowledge-base service key.

            provider_prices = INSTANCE_KNOWLEDGE_BASE.get(provider, {})

            for service_data in provider_prices.values():
                if not isinstance(service_data, dict):
                    continue

                # Current instance price
                if current_price_hr is None:
                    if raw_instance in service_data:
                        instance_info = service_data[raw_instance]

                        if isinstance(instance_info, dict):
                            current_price_hr = instance_info.get('price_hr')

                    elif instance_type in service_data:
                        instance_info = service_data[instance_type]

                        if isinstance(instance_info, dict):
                            current_price_hr = instance_info.get('price_hr')

                # Recommended instance price
                if recommended_price_hr is None and recommended in service_data:
                    recommended_info = service_data[recommended]

                    if isinstance(recommended_info, dict):
                        recommended_price_hr = recommended_info.get('price_hr')


            # Calculate savings only when both prices are available
            if (
                current_price_hr is not None
                and recommended_price_hr is not None
                and current_price_hr > 0
            ):
                # Percentage reduction in hourly price
                savings_pct = (
                    (current_price_hr - recommended_price_hr)
                    / current_price_hr
                ) * 100

                # Do not allow negative savings
                savings_pct = max(0, savings_pct)

                # Apply the calculated percentage to the actual
                # cost present in the uploaded dataset.
                savings_amount = cost * (savings_pct / 100)

            else:
                # Price information is unavailable for this particular
                # instance/recommendation pair.
                # Keep the recommendation, but do not invent savings.
                savings_pct = 0
                savings_amount = 0
            recommendations.append({
                        'type': f'{provider} {compute_service_normalized} Right-Sizing',
                        'description': f"Change {instance_type} to {recommended}",
                        'reason': f"Resource '{resource_name[:30]}...' has {util}% utilization",
                        'potential_savings': round(savings_amount, 2)
                        
                    })

    recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)

    # Return empty list instead of message dictionary
    return recommendations

# ============================================================================
# CORE ANALYSIS ENGINE
# ============================================================================

def analyze_cloud_costs(df, provider=None, filename=None):
    """
    Main analysis engine - processes data and generates insights
    """
    # Store original provider before detection
    user_selected_provider = provider
    
    # Step 1: Data validation and cleaning
    validation_result = validate_and_score_data(df)
    cleaned_df = validation_result['cleaned_df']
    
        # Step 2: ALWAYS detect provider from uploaded data/file
    # The actual detected provider takes priority over the
    # provider selected manually from the dropdown.

    detection_result = detect_provider_from_data(cleaned_df)
    detected_provider = detection_result['provider']

    # If the uploaded data identifies a provider, always use it.
    if detected_provider != 'Unknown':
        provider = detected_provider

    # If detection fails, use the user's manual selection as fallback.
    elif user_selected_provider and user_selected_provider != 'Auto-detect':
        provider = user_selected_provider

    # If neither detection nor manual selection is available,
    # keep provider as Unknown.
    else:
        provider = 'Unknown'
    
    # Check for provider mismatch
    if provider == 'Unknown' and user_selected_provider != 'Auto-detect' and user_selected_provider is not None:
        return {
            'summary': {},
            'provider': user_selected_provider,
            'error': f'Cannot provide analysis because the data does not appear to be from {user_selected_provider}. '
                     f'Please check if you selected the correct cloud provider or use Auto-detect.',
            'data_quality': {
                'score': validation_result['quality_score'],
                'warnings': validation_result['warnings'],
                'total_rows': validation_result['total_rows'],
                'valid_rows': validation_result['valid_rows']
            }
        }
    elif provider == 'Unknown':
        return {
            'summary': {},
            'provider': 'Unknown',
            'error': 'Could not detect cloud provider from your data. '
                     'Please manually select your cloud provider from the dropdown.',
            'data_quality': {
                'score': validation_result['quality_score'],
                'warnings': validation_result['warnings'],
                'total_rows': validation_result['total_rows'],
                'valid_rows': validation_result['valid_rows']
            }
        }
    
    # Step 3: Calculate summary statistics
    total_cost = cleaned_df['Cost'].sum()
    total_resources = len(cleaned_df)
    
    if 'Utilization' in cleaned_df.columns:
        avg_utilization = cleaned_df['Utilization'].mean()
        low_utilization = (cleaned_df['Utilization'] < 40).sum()
        high_utilization = (cleaned_df['Utilization'] > 70).sum()
    else:
        avg_utilization = 50
        low_utilization = 0
        high_utilization = 0
    
    # Step 4: Get top cost drivers
    top_expensive = cleaned_df.nlargest(10, 'Cost')[['ResourceName', 'Cost', 'Service', 'Utilization' if 'Utilization' in cleaned_df.columns else None]].dropna(axis=1, how='all')
    
    # Step 5: Get least utilized resources
    if 'Utilization' in cleaned_df.columns:
        least_utilized = cleaned_df.nsmallest(10, 'Utilization')[['ResourceName', 'Utilization', 'Cost', 'Service']]
    else:
        least_utilized = pd.DataFrame()
    
    # Step 6: Cost by service category
    if 'Service' in cleaned_df.columns:
        service_costs = cleaned_df.groupby('Service')['Cost'].sum().sort_values(ascending=False)
        top_services = service_costs.head(8)
    else:
        top_services = pd.Series()
    
    # Step 7: Cost by department
    if 'Department' in cleaned_df.columns:
        dept_costs = cleaned_df.groupby('Department')['Cost'].sum().sort_values(ascending=False)
    else:
        dept_costs = pd.Series()
    
    # Step 7.5: Calculate department utilization ranking
    department_utilization_ranking = {}
    if 'Department' in cleaned_df.columns and 'Utilization' in cleaned_df.columns:
        valid_util_df = cleaned_df[cleaned_df['Utilization'].notna()]
        
        if not valid_util_df.empty and 'Department' in valid_util_df.columns:
            dept_utilization = valid_util_df.groupby('Department')['Utilization'].mean()
            dept_utilization = dept_utilization[dept_utilization.notna()]
            
            if not dept_utilization.empty:
                dept_utilization = dept_utilization.round(1)
                dept_utilization_sorted = dept_utilization.sort_values(ascending=True)
                department_utilization_ranking = dept_utilization_sorted.to_dict()
    
    # Step 8: Generate specific recommendations
    analysis_summary = {
        'total_cost': round(total_cost, 2),
        'total_resources': total_resources,
        'avg_utilization': round(avg_utilization, 1),
        'low_utilization_count': int(low_utilization),
        'high_utilization_count': int(high_utilization),
        'cost_per_resource': round(total_cost / max(total_resources, 1), 2)
    }
    
    recommendations = generate_specific_recommendations(cleaned_df, provider, analysis_summary)
    
    # Calculate total potential savings - FIXED: Use .get() to handle missing keys
    total_potential_savings = sum(rec.get('potential_savings', 0) for rec in recommendations)
    
    # Step 9: Generate chart data
    chart_data = {}
    
    if not top_services.empty:
        chart_data['service_costs'] = {
            'labels': top_services.index.tolist(),
            'values': top_services.values.tolist(),
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7B76D']
        }
    
    if not dept_costs.empty and len(dept_costs) > 1:
        chart_data['department_costs'] = {
            'labels': dept_costs.index.tolist(),
            'values': dept_costs.values.tolist(),
            'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#8AC926', '#1982C4']
        }
    
    # Step 10: Future projections if multi-month data
    future_predictions = None
    has_multi_month = False

    if 'Date' in cleaned_df.columns:
        try:
            # Convert dates into monthly periods
            cleaned_df['Month'] = pd.to_datetime(
                cleaned_df['Date']
            ).dt.to_period('M')

            # Count unique months in the uploaded data
            unique_months = cleaned_df['Month'].nunique()

            # Require at least 3 months of historical data
            if unique_months >= 3:
                has_multi_month = True

                # Calculate total cloud cost for each month
                monthly_trend = cleaned_df.groupby('Month')['Cost'].sum()

                # Make sure we actually have at least 3 monthly values
                if len(monthly_trend) >= 3:

                    # ---------------------------------------------------------
                    # COMPOUND MONTHLY GROWTH RATE
                    # ---------------------------------------------------------
                    #
                    # If there are N months, there are N-1 growth intervals.
                    #
                    # Example:
                    # Month 1 -> Month 2 -> Month 3
                    #        1 growth     1 growth
                    #        interval     interval
                    #
                    growth_rate = (
                        monthly_trend.iloc[-1] /
                        monthly_trend.iloc[0]
                    ) ** (
                        1 / (len(monthly_trend) - 1)
                    )

                    # ---------------------------------------------------------
                    # CURRENT MONTHLY COST
                    # ---------------------------------------------------------
                    # Cost of the latest month in the uploaded data
                    current_monthly = monthly_trend.iloc[-1]

                    # ---------------------------------------------------------
                    # AVERAGE MONTHLY COST
                    # ---------------------------------------------------------
                    # Average cost across all available historical months
                    average_monthly = monthly_trend.mean()

                    # ---------------------------------------------------------
                    # NEXT MONTH PROJECTION
                    # ---------------------------------------------------------
                    projected_next_month = (
                        current_monthly * growth_rate
                    )

                    # ---------------------------------------------------------
                    # NEXT QUARTER PROJECTION
                    # ---------------------------------------------------------
                    # Calculate the projected cost for each of the
                    # next three months and add them together.
                    projected_month_1 = (
                        current_monthly * growth_rate
                    )

                    projected_month_2 = (
                        current_monthly * (growth_rate ** 2)
                    )

                    projected_month_3 = (
                        current_monthly * (growth_rate ** 3)
                    )

                    # Total projected expenditure for the next 3 months
                    projected_next_quarter = (
                        projected_month_1 +
                        projected_month_2 +
                        projected_month_3
                    )

                    # ---------------------------------------------------------
                    # STORE FUTURE PROJECTION RESULTS
                    # ---------------------------------------------------------
                    future_predictions = {
                        'current_monthly': round(
                            float(current_monthly), 2
                        ),

                        'average_monthly': round(
                            float(average_monthly), 2
                        ),

                        'next_month': round(
                            float(projected_next_month), 2
                        ),

                        'next_quarter': round(
                            float(projected_next_quarter), 2
                        ),

                        'growth_rate_percent': round(
                            (growth_rate - 1) * 100, 1
                        ),

                        'months_analyzed': unique_months
                    }

        except Exception:
            pass
    
    # Prepare analysis results
    analysis_results = {
        'summary': analysis_summary,
        'provider': provider,
        'top_expensive_resources': top_expensive.to_dict('records'),
        'least_utilized_resources': least_utilized.to_dict('records') if not least_utilized.empty else [],
        'service_cost_distribution': top_services.to_dict() if not top_services.empty else {},
        'department_utilization_ranking': department_utilization_ranking,
        'recommendations': recommendations,
        'total_potential_savings': round(total_potential_savings, 2),
        'savings_percentage': round((total_potential_savings / total_cost * 100), 1) if total_cost > 0 else 0,
        'data_quality': {
            'score': validation_result['quality_score'],
            'warnings': validation_result['warnings'],
            'total_rows': validation_result['total_rows'],
            'valid_rows': validation_result['valid_rows']
        },
        'chart_data': chart_data,
        'future_predictions': future_predictions,
        'has_multi_month': has_multi_month,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return analysis_results

# ============================================================================
# PDF GENERATION FUNCTION (Updated with Department Ranking)
# ============================================================================

def generate_pdf_report(analysis_data):
    """
    Generate a professional, dynamic PDF report for CloudOptix.

    Layout behavior:
    - Keeps headings with their corresponding tables.
    - Prevents major sections from being split unnecessarily.
    - Automatically moves a complete section to the next page
      when there is not enough room.
    - Keeps individual recommendations together where possible.
    - Adds a border and page number to every page.
    """

    buffer = BytesIO()

    # -------------------------------------------------------------------------
    # PAGE SETTINGS
    # -------------------------------------------------------------------------
    PAGE_WIDTH, PAGE_HEIGHT = letter

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=42,
        leftMargin=42,
        topMargin=45,
        bottomMargin=45,
        title="CloudOptix Report",
        author="CloudOptix"
    )

    styles = getSampleStyleSheet()

    # -------------------------------------------------------------------------
    # CUSTOM STYLES
    # -------------------------------------------------------------------------

    title_style = ParagraphStyle(
        'CloudOptixTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0d6efd'),
        alignment=0,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'CloudOptixSubtitle',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=4
    )

    heading_style = ParagraphStyle(
        'CloudOptixHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#198754'),
        spaceBefore=0,
        spaceAfter=8,
        keepWithNext=True
    )

    subheading_style = ParagraphStyle(
        'CloudOptixSubHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#495057'),
        spaceBefore=0,
        spaceAfter=5,
        keepWithNext=True
    )

    normal_style = ParagraphStyle(
        'CloudOptixNormal',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#343a40'),
        spaceAfter=4
    )

    small_style = ParagraphStyle(
        'CloudOptixSmall',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=3
    )

    savings_style = ParagraphStyle(
        'CloudOptixSavings',
        parent=normal_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#198754'),
        spaceAfter=3
    )

    # -------------------------------------------------------------------------
    # PAGE BORDER + PAGE NUMBER
    # -------------------------------------------------------------------------

    def add_page_decoration(canvas, doc):
        canvas.saveState()

        # Page border
        canvas.setStrokeColor(colors.HexColor('#212529'))
        canvas.setLineWidth(2)

        canvas.rect(
            18,
            18,
            PAGE_WIDTH - 36,
            PAGE_HEIGHT - 36
        )

        # Page number
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6c757d'))

        canvas.drawCentredString(
            PAGE_WIDTH / 2,
            27,
            f"CloudOptix  |  Page {canvas.getPageNumber()}"
        )

        canvas.restoreState()

    # -------------------------------------------------------------------------
    # CONTENT
    # -------------------------------------------------------------------------

    content = []

    # =========================================================================
    # REPORT HEADER
    # =========================================================================

    header_block = [
        Paragraph("CloudOptix Report", title_style),

        Paragraph(
            "Intelligent Cloud Cost Optimizer",
            subtitle_style
        ),

        Paragraph(
            f"Generated on: {analysis_data.get('analysis_date', 'N/A')}",
            normal_style
        ),

        Paragraph(
            f"Cloud Provider: {analysis_data.get('provider', 'Unknown')}",
            normal_style
        ),

        Spacer(1, 10)
    ]

    content.append(
        KeepTogether(header_block)
    )

    # =========================================================================
    # EXECUTIVE SUMMARY
    # =========================================================================

    summary_data = analysis_data.get('summary', {})

    summary_table_data = [
        ['Metric', 'Value'],

        [
            'Total Monthly Cost',
            f"${summary_data.get('total_cost', 0):,.2f}"
        ],

        [
            'Total Resources Analyzed',
            f"{summary_data.get('total_resources', 0)}"
        ],

        [
            'Average Utilization',
            f"{summary_data.get('avg_utilization', 0)}%"
        ],

        [
            'Underutilized Resources (<40%)',
            f"{summary_data.get('low_utilization_count', 0)}"
        ],

        [
            'Potential Monthly Savings',
            f"${analysis_data.get('total_potential_savings', 0):,.2f}"
        ],

        [
            'Savings Percentage',
            f"{analysis_data.get('savings_percentage', 0)}%"
        ]
    ]

    summary_table = Table(
        summary_table_data,
        colWidths=[340, 170],
        repeatRows=1
    )

    summary_table.setStyle(
        TableStyle([
            (
                'BACKGROUND',
                (0, 0),
                (-1, 0),
                colors.HexColor('#0d6efd')
            ),

            (
                'TEXTCOLOR',
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                'FONTNAME',
                (0, 0),
                (-1, 0),
                'Helvetica-Bold'
            ),

            (
                'FONTNAME',
                (0, 1),
                (0, -1),
                'Helvetica-Bold'
            ),

            (
                'ALIGN',
                (1, 1),
                (1, -1),
                'RIGHT'
            ),

            (
                'ALIGN',
                (0, 0),
                (0, 0),
                'LEFT'
            ),

            (
                'BACKGROUND',
                (0, 1),
                (-1, -1),
                colors.HexColor('#F8FAFC')
            ),

            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor('#DDE3EA')
            ),

            (
                'FONTSIZE',
                (0, 0),
                (-1, -1),
                9
            ),

            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                6
            ),

            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    content.append(
        KeepTogether([
            Paragraph("Executive Summary", heading_style),
            summary_table,
            Spacer(1, 14)
        ])
    )

    # =========================================================================
    # TOP COST DRIVERS
    # =========================================================================

    top_expensive_resources = analysis_data.get(
        'top_expensive_resources',
        []
    )

    if top_expensive_resources:

        top_costs_data = [
            [
                'Resource Name',
                'Service',
                'Monthly Cost',
                'Utilization'
            ]
        ]

        for resource in top_expensive_resources[:10]:

            resource_name = str(
                resource.get('ResourceName', 'Unknown')
            )

            if len(resource_name) > 30:
                resource_name = resource_name[:30] + '...'

            service = str(
                resource.get('Service', 'Unknown')
            )

            if len(service) > 20:
                service = service[:20] + '...'

            util = resource.get(
                'Utilization',
                'N/A'
            )

            util_str = (
                f"{util}%"
                if util != 'N/A'
                else 'N/A'
            )

            cost = resource.get(
                'Cost',
                0
            )

            top_costs_data.append([
                resource_name,
                service,
                f"${cost:,.2f}",
                util_str
            ])

        top_costs_table = Table(
            top_costs_data,
            colWidths=[220, 120, 100, 70],
            repeatRows=1
        )

        top_costs_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#dc3545')
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'ALIGN',
                    (2, 1),
                    (-1, -1),
                    'RIGHT'
                ),

                (
                    'ALIGN',
                    (0, 0),
                    (1, -1),
                    'LEFT'
                ),

                (
                    'BACKGROUND',
                    (0, 1),
                    (-1, -1),
                    colors.HexColor('#FFF8F8')
                ),

                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor('#DEE2E6')
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8.5
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        # IMPORTANT:
        # Heading + table are kept together.
        # If they don't fit in remaining page space,
        # ReportLab moves the complete section to the next page.

        content.append(
            KeepTogether([
                Paragraph(
                    "Top 10 Cost Drivers",
                    heading_style
                ),

                top_costs_table,

                Spacer(1, 12)
            ])
        )

    # =========================================================================
    # TOP UNDERUTILIZED RESOURCES
    # =========================================================================

    least_utilized_resources = analysis_data.get(
        'least_utilized_resources',
        []
    )

    if least_utilized_resources:

        underutilized_data = [
            [
                'Resource Name',
                'Utilization',
                'Monthly Cost',
                'Action'
            ]
        ]

        for resource in least_utilized_resources[:10]:

            resource_name = str(
                resource.get(
                    'ResourceName',
                    'Unknown'
                )
            )

            if len(resource_name) > 30:
                resource_name = resource_name[:30] + '...'

            util = resource.get(
                'Utilization',
                0
            )

            if util < 10:
                action = 'STOP'
            elif util < 30:
                action = 'DOWNSIZE'
            else:
                action = 'MONITOR'

            cost = resource.get(
                'Cost',
                0
            )

            underutilized_data.append([
                resource_name,
                f"{util}%",
                f"${cost:,.2f}",
                action
            ])

        underutilized_table = Table(
            underutilized_data,
            colWidths=[220, 90, 110, 90],
            repeatRows=1
        )

        underutilized_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#ffc107')
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.black
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'ALIGN',
                    (1, 1),
                    (-1, -1),
                    'CENTER'
                ),

                (
                    'ALIGN',
                    (0, 1),
                    (0, -1),
                    'LEFT'
                ),

                (
                    'BACKGROUND',
                    (0, 1),
                    (-1, -1),
                    colors.HexColor('#FFFCF2')
                ),

                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor('#DEE2E6')
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8.5
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        content.append(
            KeepTogether([
                Paragraph(
                    "Top 10 Underutilized Resources",
                    heading_style
                ),

                underutilized_table,

                Spacer(1, 12)
            ])
        )

    # =========================================================================
    # DEPARTMENT UTILIZATION RANKING
    # =========================================================================

    department_ranking = analysis_data.get(
        'department_utilization_ranking',
        {}
    )

    if department_ranking:

        dept_data = [
            [
                'Rank',
                'Department',
                'Avg Utilization',
                'Status'
            ]
        ]

        sorted_depts = sorted(
            department_ranking.items(),
            key=lambda x: x[1]
        )

        for rank, (dept, util) in enumerate(
            sorted_depts,
            1
        ):

            dept = str(dept)

            if len(dept) > 25:
                dept = dept[:25] + '...'

            if util >= 70:
                status = 'Optimal'
            elif util >= 40:
                status = 'Moderate'
            else:
                status = 'Needs Attention'

            dept_data.append([
                str(rank),
                dept,
                f"{util}%",
                status
            ])

        dept_table = Table(
            dept_data,
            colWidths=[55, 210, 120, 125],
            repeatRows=1
        )

        dept_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#6f42c1')
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER'
                ),

                (
                    'BACKGROUND',
                    (0, 1),
                    (-1, -1),
                    colors.HexColor('#FAF8FF')
                ),

                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor('#DEE2E6')
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8.5
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        content.append(
            KeepTogether([
                Paragraph(
                    "Department Utilization Ranking",
                    heading_style
                ),

                dept_table,

                Spacer(1, 12)
            ])
        )

    # =========================================================================
    # OPTIMIZATION RECOMMENDATIONS
    # =========================================================================

    recommendations = analysis_data.get(
        'recommendations',
        []
    )

    recommendation_section = [
        Paragraph(
            "Optimization Recommendations",
            heading_style
        )
    ]

    if recommendations:

        for i, rec in enumerate(
            recommendations,
            1
        ):

            recommendation_type = rec.get(
                'type',
                'Recommendation'
            )

            description = rec.get(
                'description',
                'N/A'
            )

            reason = rec.get(
                'reason',
                'N/A'
            )

            savings = rec.get(
                'potential_savings',
                0
            )

            recommendation_block = [
                Paragraph(
                    f"{i}. {recommendation_type}",
                    subheading_style
                ),

                Paragraph(
                    f"<b>Recommendation:</b> {description}",
                    normal_style
                ),

                Paragraph(
                    f"<b>Reason:</b> {reason}",
                    normal_style
                ),

                Paragraph(
                    f"Potential Savings: ${savings:,.2f}/month",
                    savings_style
                ),

                Spacer(1, 7)
            ]

            # Each recommendation is kept together where possible.
            recommendation_section.append(
                KeepTogether(
                    recommendation_block
                )
            )

    else:

        recommendation_section.append(
            Paragraph(
                "No specific recommendations generated. "
                "All resources appear properly sized.",
                normal_style
            )
        )

    content.append(
        KeepTogether(
            recommendation_section[:1]
        )
    )

    # Add recommendation blocks separately so that
    # one very long recommendation does not prevent
    # the following recommendations from flowing naturally.
    for block in recommendation_section[1:]:
        content.append(block)

    # =========================================================================
    # FUTURE COST PROJECTIONS
    # =========================================================================

    projections = analysis_data.get(
        'future_predictions'
    )

    if projections:

        projection_data = [
            ['Metric', 'Value'],

            [
                'Current Monthly Cost',
                f"${projections.get('current_monthly', 0):,.2f}"
            ],

            [
                'Average Monthly Cost',
                f"${projections.get('average_monthly', 0):,.2f}"
            ],

            [
                'Projected Next Month',
                f"${projections.get('next_month', 0):,.2f}"
            ],

            [
                'Projected Next Quarter',
                f"${projections.get('next_quarter', 0):,.2f}"
            ],

            [
                'Monthly Growth Rate',
                f"{projections.get('growth_rate_percent', 0):+.1f}%"
            ],

            [
                'Historical Months Analyzed',
                str(projections.get('months_analyzed', 0))
            ]
        ]

        projection_table = Table(
            projection_data,
            colWidths=[300, 210],
            repeatRows=1
        )

        projection_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#0dcaf0')
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.black
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'FONTNAME',
                    (0, 1),
                    (0, -1),
                    'Helvetica-Bold'
                ),

                (
                    'ALIGN',
                    (1, 1),
                    (1, -1),
                    'RIGHT'
                ),

                (
                    'BACKGROUND',
                    (0, 1),
                    (-1, -1),
                    colors.HexColor('#F8FAFC')
                ),

                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor('#DEE2E6')
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    6
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        projection_basis = Paragraph(
            f"Projection basis: Historical monthly cloud "
            f"expenditure was analyzed across "
            f"{projections.get('months_analyzed', 0)} months. "
            f"The calculated monthly growth trend was used "
            f"to estimate the next month and the total cost "
            f"of the following three months.",
            small_style
        )

        content.append(
            KeepTogether([
                Paragraph(
                    "Future Cost Projections",
                    heading_style
                ),

                projection_table,

                Spacer(1, 8),

                projection_basis,

                Spacer(1, 10)
            ])
        )

    # =========================================================================
    # REPORT FOOTER CONTENT
    # =========================================================================

    content.append(
        Spacer(1, 10)
    )

    content.append(
        Paragraph(
            "Generated by CloudOptix",
            ParagraphStyle(
                'PDF_Footer_Main',
                parent=normal_style,
                fontSize=9,
                textColor=colors.HexColor('#6c757d'),
                alignment=1,
                spaceAfter=3
            )
        )
    )

    content.append(
        Paragraph(
            "© CloudOptix - All Rights Reserved",
            ParagraphStyle(
                'PDF_Footer_Copyright',
                parent=normal_style,
                fontSize=7.5,
                textColor=colors.HexColor('#9AA0A6'),
                alignment=1
            )
        )
    )

    # =========================================================================
    # BUILD PDF
    # =========================================================================

    doc.build(
        content,
        onFirstPage=add_page_decoration,
        onLaterPages=add_page_decoration
    )

    # -------------------------------------------------------------------------
    # RETURN PDF DATA
    # -------------------------------------------------------------------------

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data

# ============================================================================
# FLASK ROUTES (Updated with provider validation)
# ============================================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudOptix</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --primary-color: #0d6efd;
            --secondary-color: #6c757d;
            --success-color: #198754;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --info-color: #0dcaf0;
        }
        
        body {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding-bottom: 50px;
        }
        
        .header-gradient {
            background: linear-gradient(135deg, var(--primary-color) 0%, #0a58ca 100%);
            color: white;
            padding: 30px 0;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 5px 20px rgba(13, 110, 253, 0.2);
        }
        
        .feature-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        }
        
        
    /* Add this to your CSS section */
    .stat-card {
        color: white;
        padding: 15px;  /* Reduced padding */
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
        height: 230px;  /* Fixed height for consistency */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stat-card.primary { background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%); }
    .stat-card.success { background: linear-gradient(135deg, #198754 0%, #157347 100%); }
    .stat-card.warning { background: linear-gradient(135deg, #ffc107 0%, #ffca2c 100%); }
    .stat-card.danger { background: linear-gradient(135deg, #dc3545 0%, #b02a37 100%); }
    .stat-card.info { background: linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%); }
    .stat-card.secondary { background: linear-gradient(135deg, #6c757d 0%, #545b62 100%); }
    
    .stat-value {
        font-size: 1.8rem;  /* Reduced font size */
        font-weight: 700;
        margin: 5px 0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .stat-card h6 {
        font-size: 0.9rem;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    .stat-card small {
        font-size: 0.75rem;
        opacity: 0.9;
    }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 10px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .recommendation-card {
            border-left: 5px solid;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        
        .provider-badge {
            font-size: 0.8rem;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .savings-badge {
            font-size: 1.1rem;
            padding: 8px 16px;
            border-radius: 10px;
            font-weight: 600;
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.95);
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        }
        
        .quality-score {
            width: 120px;
            height: 120px;
            position: relative;
        }
        
        .quality-score-circle {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            position: absolute;
        }
        
        .quality-score-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            font-weight: bold;
        }
        
        .table-custom th {
            background: linear-gradient(135deg, var(--primary-color) 0%, #0a58ca 100%);
            color: white;
            font-weight: 600;
            border: none;
        }
        
        .table-custom tbody tr:hover {
            background-color: rgba(13, 110, 253, 0.05);
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .recommendation-header {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary-color);
        }
        
        .savings-highlight {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: 600;
            color: #155724;
        }
        
        .recommendation-simple {
            background: white;
            border-left: 4px solid var(--primary-color);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
   .provider-detection-card {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 10px 24px;
    height: 85px;
    min-height: 85px;
    background: linear-gradient(135deg, #f8fbff, #eef8ff);
    border: 1px solid #d9eaf7;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}

.provider-logo {
    width: 120px;
    height: 120px;
    object-fit: contain;
    flex-shrink: 0;
}

.provider-detection-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 2px;
}

.provider-detection-name {
    font-size: 1.45rem;
    font-weight: 700;
    color: #212529;
    line-height: 1.1;
}

.provider-detected-status {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin-left: 10px;
    padding: 4px 10px;
    border-radius: 20px;
    background: #d9f5e5;
    color: #198754;
    font-size: 0.75rem;
    font-weight: 600;
}

/* ==========================================
   CLOUDOPTIX HERO HEADER
   ========================================== */

.cloudoptix-header {
    width: 100%;
    background: linear-gradient(
        135deg,
        #1769e8 0%,
        #0d5edb 50%,
        #155dcc 100%
    );

    padding: 18px 6%;
    border-radius: 0 0 18px 18px;

    box-shadow:
        0 8px 25px rgba(13, 94, 219, 0.18);

    color: white;
}

.cloudoptix-header-inner {
    max-width: 1500px;
    margin: 0 auto;

    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 40px;
}


/* ==========================================
   CLOUDOPTIX BRAND
   ========================================== */

.cloudoptix-brand {
    display: flex;
    align-items: center;
    gap: 18px;
}

.cloudoptix-symbol {
    width: 160px;
    height: 130px;
    object-fit: contain;
    flex-shrink: 0;
}

.cloudoptix-brand-text h1 {
    margin: 0;

    font-size: 3.4rem;
    font-weight: 700;

    letter-spacing: -1.8px;
    line-height: 1.05;
}

.cloud-text {
    color: #ffffff;
}

.optix-text {
    color: #4dabff;
}

.cloudoptix-brand-text p {
    margin: 8px 0 0;

    font-size: 1.25rem;
    font-weight: 400;

    letter-spacing: 0.2px;

    color: rgba(255, 255, 255, 0.95);
}


/* ==========================================
   FEATURE PILL
   ========================================== */

.cloudoptix-features {
    display: flex;
    align-items: center;

    gap: 12px;

    padding: 14px 28px;

    background: #ffffff;

    border-radius: 40px;

    font-size: 1.05rem;
    font-weight: 700;

    white-space: nowrap;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.12);
}

.feature-blue {
    color: #0d6efd;
}

.feature-green {
    color: #087f5b;
}

.feature-red {
    color: #dc3545;
}

.feature-dot {
    color: #777777;
    font-weight: 500;
}


/* ==========================================
   RESPONSIVE
   ========================================== */

@media (max-width: 900px) {

    .cloudoptix-header-inner {
        flex-direction: column;
        align-items: flex-start;
    }

    .cloudoptix-features {
        align-self: stretch;
        justify-content: center;
    }
}


@media (max-width: 600px) {

    .cloudoptix-header {
        padding: 18px 5%;
    }

    .cloudoptix-brand {
        gap: 12px;
    }

    .cloudoptix-symbol {
        width: 55px;
        height: 55px;
    }

    .cloudoptix-brand-text h1 {
        font-size: 2.2rem;
    }

    .cloudoptix-brand-text p {
        font-size: 1rem;
        margin-top: 6px;
    }

    .cloudoptix-features {
        font-size: 0.85rem;
        padding: 11px 16px;
        gap: 7px;
    }
}
}


    </style>
</head>
<body>
    <!-- CloudOptix Hero Header -->
<header class="cloudoptix-header">
    <div class="cloudoptix-header-inner">

        <!-- CloudOptix Branding -->
        <div class="cloudoptix-brand">

    <img
        src="{{ url_for('static', filename='provider-logos/cloudoptix-symbol.png') }}"
        alt="CloudOptix"
        class="cloudoptix-symbol"
    >

    <div class="cloudoptix-brand-text">
        <h1>
            <span class="cloud-text">Cloud</span><span class="optix-text">Optix</span>
        </h1>

        <p>Intelligent Cloud Cost Optimizer</p>
    </div>

</div>

        <!-- Feature Highlights -->
        <div class="cloudoptix-features">
            <span class="feature-blue">5 Providers</span>
            <span class="feature-dot">•</span>
            <span class="feature-green">Auto-Detect</span>
            <span class="feature-dot">•</span>
            <span class="feature-red">Specific Sizing</span>
        </div>

    </div>
</header>

    <!-- Main Container -->
    <div class="container mt-5">
        <!-- Upload Section -->
        <div class="feature-card pulse-animation">
            <div class="row">
                <div class="col-md-8">
                    <h3 class="fw-bold mb-3"><i class="fas fa-cloud-upload-alt text-primary me-2"></i>Upload Your Cloud Cost Data</h3>
                    <p class="text-muted">Upload CSV or Excel files with your cloud costs. We'll auto-detect your provider and generate specific optimization recommendations.</p>
                </div>
                <div class="col-md-4">
                    <form id="uploadForm" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="fileInput" class="form-label fw-bold">Select File</label>
                            <input class="form-control form-control-lg" type="file" id="fileInput" accept=".csv,.xlsx,.xls" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="providerSelect" class="form-label fw-bold">Cloud Provider</label>
                            <select class="form-select form-select-lg" id="providerSelect">
                                <option value="Auto-detect">Auto-detect (Recommended)</option>
                                <option value="AWS">Amazon Web Services</option>
                                <option value="Azure">Microsoft Azure</option>
                                <option value="GCP">Google Cloud Platform</option>
                                <option value="Oracle">Oracle Cloud</option>
                                <option value="IBM">IBM Cloud</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn btn-success btn-lg w-100 mt-2">
                            <i class="fas fa-bolt me-2"></i>Analyze & Optimize
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <!-- Loading Overlay -->
        <div id="loading" class="loading-overlay">
            <div class="text-center">
                <div class="spinner-border text-primary" style="width: 4rem; height: 4rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h3 class="mt-4 text-primary">Analyzing Your Cloud Costs</h3>
                <p class="text-muted">Generating specific, actionable recommendations...</p>
                <div class="progress mt-3" style="height: 6px; width: 300px; margin: 0 auto;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%"></div>
                </div>
            </div>
        </div>

        <!-- Data Quality Alerts -->
        <div id="dataQualityAlerts" style="display: none;"></div>

        <!-- Results Container -->
        <div id="resultsContainer"></div>

        <!-- Features Section -->
        <div class="row mt-5">
            <div class="col-md-12">
                <h3 class="fw-bold mb-4 text-center">🎯 Advanced Features</h3>
            </div>
            
            <div class="col-md-4">
                <div class="feature-card text-center">
                    <div class="bg-primary bg-opacity-10 rounded-circle p-4 d-inline-block mb-3">
                        <i class="fas fa-robot fa-3x text-primary"></i>
                    </div>
                    <h5 class="fw-bold">Auto Provider Detection</h5>
                    <p class="text-muted">Automatically detects AWS, Azure, GCP, Oracle, and IBM Cloud from your data.</p>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="feature-card text-center">
                    <div class="bg-success bg-opacity-10 rounded-circle p-4 d-inline-block mb-3">
                        <i class="fas fa-exchange-alt fa-3x text-success"></i>
                    </div>
                    <h5 class="fw-bold">Specific Sizing Recommendations</h5>
                    <p class="text-muted">Exact recommendations like "Change from m5.xlarge to m5.large" with specific savings.</p>
                </div>
            </div>
            
            <!-- Replace the Future Cost Projections box with PDF Generation box -->
<div class="col-md-4">
    <div class="feature-card text-center">
        <div class="bg-warning bg-opacity-10 rounded-circle p-4 d-inline-block mb-3">
            <i class="fas fa-file-pdf fa-3x text-warning"></i>  <!-- Changed to PDF icon -->
        </div>
        <h5 class="fw-bold">Professional PDF Reports</h5>  <!-- Changed title -->
        <p class="text-muted">Generate comprehensive PDF reports with detailed analysis and recommendations.</p>  <!-- Changed description -->
    </div>
</div>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    <script>
        let currentAnalysisData = null;
        
        // Format numbers with commas
        function formatNumber(num) {
            if (typeof num !== 'number') num = parseFloat(num) || 0;
            return num.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        // Format large numbers in K, M, B format
        function formatLargeNumber(num) {
            if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B';
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toFixed(0);
        }
        
        // Calculate quality score color
        function getQualityColor(score) {
            if (score >= 80) return 'success';
            if (score >= 60) return 'warning';
            return 'danger';
        }
        
        // Handle form submission
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('fileInput');
            const providerSelect = document.getElementById('providerSelect');
            
            if (!fileInput.files.length) {
                alert('Please select a file first!');
                return;
            }
            
            const file = fileInput.files[0];
            const provider = providerSelect.value;
            
            // Show loading
            document.getElementById('loading').style.display = 'flex';
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('provider', provider);
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    // Clear previous results
                    document.getElementById('resultsContainer').innerHTML = '';
                    document.getElementById('dataQualityAlerts').innerHTML = '';
                    document.getElementById('dataQualityAlerts').style.display = 'none';
                    
                    // Store analysis data
                    currentAnalysisData = result.analysis;
                    
                    // Display data quality warnings if any
                    if (result.analysis.data_quality && result.analysis.data_quality.warnings.length > 0) {
                        displayDataQualityWarnings(result.analysis.data_quality);
                    }
                    
                    // Display results
                    displayAnalysisResults(result.analysis);
                    
                    // Scroll to results
                    setTimeout(() => {
                        document.getElementById('resultsContainer').scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }, 100);
                    
                } else {
                    throw new Error(result.error || 'Analysis failed');
                }
                
            } catch (error) {
                console.error('Error:', error);
                showError('Analysis failed: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });
        
        // Display data quality warnings
        function displayDataQualityWarnings(dataQuality) {
            let html = `
                <div class="feature-card mb-4">
                    <div class="row align-items-center">
                        <div class="col-md-3 text-center">
                            <div class="quality-score mx-auto mb-3">
                                <svg width="120" height="120" viewBox="0 0 120 120">
                                    <circle cx="60" cy="60" r="54" fill="none" stroke="#e9ecef" stroke-width="12"/>
                                    <circle cx="60" cy="60" r="54" fill="none" stroke="var(--${getQualityColor(dataQuality.score)}-color)" 
                                            stroke-width="12" stroke-linecap="round" 
                                            stroke-dasharray="${dataQuality.score * 3.39}" 
                                            stroke-dashoffset="339" transform="rotate(-90 60 60)"/>
                                </svg>
                                <div class="quality-score-text">
                                    ${dataQuality.score}/100
                                </div>
                            </div>
                            <div class="badge bg-${getQualityColor(dataQuality.score)} fs-6">Data Quality</div>
                        </div>
                        <div class="col-md-9">
                            <h4 class="fw-bold mb-3"><i class="fas fa-clipboard-check me-2"></i>Data Quality Report</h4>
                            <p class="text-muted mb-3">${dataQuality.valid_rows} of ${dataQuality.total_rows} rows contain valid cost data.</p>
            `;
            
            dataQuality.warnings.forEach((warning, index) => {
                const icon = warning.level === 'high' ? 'exclamation-triangle' : 
                            warning.level === 'medium' ? 'exclamation-circle' : 'info-circle';
                const color = warning.level === 'high' ? 'danger' : 
                             warning.level === 'medium' ? 'warning' : 'info';
                
                html += `
                    <div class="alert alert-${color} alert-dismissible fade show mb-2" role="alert">
                        <i class="fas fa-${icon} me-2"></i>
                        <strong>${warning.level.toUpperCase()}:</strong> ${warning.message}
                        ${warning.suggestion ? `<div class="mt-1 small"><i class="fas fa-lightbulb me-1"></i>${warning.suggestion}</div>` : ''}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
            });
            
            html += `</div></div></div>`;
            
            document.getElementById('dataQualityAlerts').innerHTML = html;
            document.getElementById('dataQualityAlerts').style.display = 'block';
        }
        
        // Display analysis results
        function displayAnalysisResults(analysis) {
            let html = '';
            
            // ============================================================
// COST ANALYSIS SUMMARY + DETECTED CLOUD PROVIDER
// ============================================================

const providerLogos = {
    "AWS": "/static/provider-logos/aws.png",
    "Azure": "/static/provider-logos/azure.png",
    "GCP": "/static/provider-logos/gcp.png",
    "Oracle": "/static/provider-logos/oracle.png",
    "IBM": "/static/provider-logos/ibm.png"
};

const providerLogo =
    providerLogos[analysis.provider] || "/static/provider-logos/cloud.png";

html += `
    <div class="feature-card mb-4">
        <div class="row align-items-center flex-nowrap">

            <!-- Cost Analysis Summary -->
            <div class="col-7">
                <h3 class="fw-bold mb-1">
                    <span style="color: #000000;">▥</span> Cost Analysis Summary
                </h3>

                <p class="text-muted mb-0">
                    Analyzed on ${analysis.analysis_date}
                </p>
            </div>

            <!-- Detected Provider -->
            <div class="col-5">
                <div class="provider-detection-card">

                    <img
                        src="${providerLogo}"
                        alt="${analysis.provider} logo"
                        class="provider-logo"
                    >

                    <div>
                        <div class="provider-detection-label">
                            Detected Cloud Provider
                        </div>

                        <div class="provider-detection-name">
                            ${analysis.provider}

                            <span class="provider-detected-status">
                                ✓ Detected
                            </span>
                        </div>
                    </div>

                </div>
            </div>

        </div>
    </div>
`;
            
            // Statistics Cards
            <!-- In the HTML_TEMPLATE, update the Statistics Cards section: -->
          <!-- Statistics Cards -->
	   html += `
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="stat-card primary">
                            <i class="fas fa-money-bill-wave fa-3x mb-3"></i>
                            <div class="stat-value">$${formatNumber(analysis.summary.total_cost)}</div>
                            <h6>Total Cost</h6>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card success">
                            <i class="fas fa-piggy-bank fa-3x mb-3"></i>
                            <div class="stat-value">$${formatNumber(analysis.total_potential_savings)}</div>
                            <h6>Potential Savings</h6>
                            <small>${analysis.savings_percentage}% of total</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card warning">
                            <i class="fas fa-server fa-3x mb-3"></i>
                            <div class="stat-value">${formatLargeNumber(analysis.summary.total_resources)}</div>
                            <h6>Resources Analyzed</h6>
                            <small>${analysis.summary.low_utilization_count} underutilized</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card info">
                            <i class="fas fa-chart-line fa-3x mb-3"></i>
                            <div class="stat-value">${analysis.summary.avg_utilization}%</div>
                            <h6>Average Utilization</h6>
                            <small>${analysis.summary.high_utilization_count} highly utilized</small>
                        </div>
                    </div>
                </div>
            `;
                        
            // Top Cost Drivers and Underutilized Resources
            html += `
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="feature-card h-100">
                            <h4 class="fw-bold mb-3 text-danger"><i class="fas fa-arrow-up me-2"></i>Top Cost Drivers</h4>
                            <div class="table-responsive">
                                <table class="table table-custom table-hover">
                                    <thead>
                                        <tr>
                                            <th>Resource</th>
                                            <th>Cost/Month</th>
                                            <th>Service</th>
                                            ${analysis.summary.avg_utilization > 0 ? '<th>Utilization</th>' : ''}
                                        </tr>
                                    </thead>
                                    <tbody>
            `;
            
            analysis.top_expensive_resources.forEach(resource => {
                const utilClass = resource.Utilization >= 70 ? 'success' : 
                                resource.Utilization >= 40 ? 'warning' : 'danger';
                
                html += `
                    <tr>
                        <td><strong>${resource.ResourceName.substring(0, 30)}${resource.ResourceName.length > 30 ? '...' : ''}</strong></td>
                        <td class="fw-bold">$${formatNumber(resource.Cost)}</td>
                        <td>${resource.Service || 'Unknown'}</td>
                        ${analysis.summary.avg_utilization > 0 ? 
                          `<td><span class="badge bg-${utilClass}">${resource.Utilization || 'N/A'}%</span></td>` : ''}
                    </tr>
                `;
            });
            
            html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="feature-card h-100">
                            <h4 class="fw-bold mb-3 text-warning"><i class="fas fa-arrow-down me-2"></i>Most Underutilized Resources</h4>
                            <div class="table-responsive">
                                <table class="table table-custom table-hover">
                                    <thead>
                                        <tr>
                                            <th>Resource</th>
                                            <th>Utilization</th>
                                            <th>Cost/Month</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            `;
            
            if (analysis.least_utilized_resources.length > 0) {
                analysis.least_utilized_resources.forEach(resource => {
                    let action = 'Monitor';
                    if (resource.Utilization < 10) action = 'CONSIDER STOPPING';
                    else if (resource.Utilization < 20) action = 'Downsize by 2';
                    else if (resource.Utilization < 30) action = 'Downsize by 1';
                    else if (resource.Utilization < 40) action = 'Consider Downsizing';
                    
                    html += `
                        <tr>
                            <td><strong>${resource.ResourceName.substring(0, 25)}${resource.ResourceName.length > 25 ? '...' : ''}</strong></td>
                            <td class="fw-bold text-danger">${resource.Utilization}%</td>
                            <td>$${formatNumber(resource.Cost)}</td>
                            <td><span class="badge bg-danger">${action}</span></td>
                        </tr>
                    `;
                });
            } else {
                html += `<tr><td colspan="4" class="text-center text-muted">No utilization data available</td></tr>`;
            }
            
            html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Cost Distribution Chart
            if (analysis.chart_data && analysis.chart_data.service_costs) {
                html += `
                    <div class="feature-card mb-4">
                        <h4 class="fw-bold mb-3"><i class="fas fa-chart-pie me-2"></i>Cost Distribution by Service</h4>
                        <div class="chart-container">
                            <div id="costChart" style="height: 400px;"></div>
                        </div>
                    </div>
                `;
            }

            // Department Cost Distribution Chart
            if (analysis.chart_data && analysis.chart_data.department_costs) {
                html += `
                    <div class="feature-card mb-4">
                        <h4 class="fw-bold mb-3"><i class="fas fa-chart-pie me-2"></i>Cost Distribution by Department</h4>
                        <div class="chart-container">
                            <div id="deptCostChart" style="height: 400px;"></div>
                        </div>
                    </div>
                `;
            }
            
            // Department Utilization Ranking
            if (analysis.department_utilization_ranking && Object.keys(analysis.department_utilization_ranking).length > 0) {
                html += `
                    <div class="feature-card mb-4">
                        <h4 class="fw-bold mb-3"><i class="fas fa-sort-amount-down me-2"></i>Department Utilization Ranking</h4>
                        <p class="text-muted">Departments sorted by average utilization (lower = more optimization needed)</p>
                        <div class="table-responsive">
                            <table class="table table-custom table-hover">
                                <thead>
                                    <tr>
                                        <th>Rank</th>
                                        <th>Department</th>
                                        <th>Average Utilization</th>
                                        <th>Status</th>
                                        <th>Recommendation</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;
                
                const sortedDepts = Object.entries(analysis.department_utilization_ranking)
                    .sort((a, b) => a[1] - b[1]);
                
                let rank = 1;
                for (const [dept, util] of sortedDepts) {
                    let utilClass, status, recommendation;
                    
                    if (util >= 70) {
                        utilClass = 'success';
                        status = 'Optimal';
                        recommendation = 'Maintain';
                    } else if (util >= 40) {
                        utilClass = 'warning';
                        status = 'Moderate';
                        recommendation = 'Review';
                    } else {
                        utilClass = 'danger';
                        status = 'Needs Attention';
                        recommendation = 'Optimize Immediately';
                    }
                    
                    html += `
                        <tr>
                            <td class="fw-bold">${rank++}</td>
                            <td><strong>${dept}</strong></td>
                            <td><span class="badge bg-${utilClass}">${util}%</span></td>
                            <td><span class="badge bg-${utilClass}">${status}</span></td>
                            <td><small class="text-${utilClass} fw-bold">${recommendation}</small></td>
                        </tr>
                    `;
                }
                
                html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }
            
            // Future Projections (if available)
if (analysis.has_multi_month && analysis.future_predictions) {

    const projection = analysis.future_predictions;

    html += `
        <div class="feature-card mb-4">

            <h4 class="fw-bold mb-3">
                <i class="fas fa-chart-line me-2"></i>
                Future Cost Projections
            </h4>

            <p class="text-muted">
                Based on ${projection.months_analyzed} months of
                historical cloud cost data
            </p>

            <div class="row mt-4">

                <!-- =====================================================
                     CURRENT MONTHLY COST
                     ===================================================== -->
                <div class="col-md-3 mb-3">
                    <div class="card border-secondary h-100">

                        <div class="card-body text-center">

                            <h5 class="card-title text-secondary">
                                Current Monthly Cost
                            </h5>

                            <div class="display-6 fw-bold text-secondary">
                                $${formatNumber(
                                    projection.current_monthly
                                )}
                            </div>

                            <p class="card-text mt-2">
                                Latest month's actual cost
                            </p>

                        </div>

                    </div>
                </div>


                <!-- =====================================================
                     AVERAGE MONTHLY COST
                     ===================================================== -->
                <div class="col-md-3 mb-3">
                    <div class="card border-info h-100">

                        <div class="card-body text-center">

                            <h5 class="card-title text-info">
                                Average Monthly Cost
                            </h5>

                            <div class="display-6 fw-bold text-info">
                                $${formatNumber(
                                    projection.average_monthly
                                )}
                            </div>

                            <p class="card-text mt-2">
                                Historical monthly average
                            </p>

                        </div>

                    </div>
                </div>


                <!-- =====================================================
                     NEXT MONTH PROJECTION
                     ===================================================== -->
                <div class="col-md-3 mb-3">
                    <div class="card border-primary h-100">

                        <div class="card-body text-center">

                            <h5 class="card-title text-primary">
                                Next Month
                            </h5>

                            <div class="display-6 fw-bold text-primary">
                                $${formatNumber(
                                    projection.next_month
                                )}
                            </div>

                            <p class="card-text mt-2">
                                Projected cost based on historical trend
                            </p>

                            <small class="text-muted">

                                ${
                                    projection.growth_rate_percent > 0
                                        ? '+'
                                        : ''
                                }${projection.growth_rate_percent}%
                                monthly growth

                            </small>

                        </div>

                    </div>
                </div>


                <!-- =====================================================
                     NEXT QUARTER PROJECTION
                     ===================================================== -->
                <div class="col-md-3 mb-3">
                    <div class="card border-warning h-100">

                        <div class="card-body text-center">

                            <h5 class="card-title text-warning">
                                Next Quarter
                            </h5>

                            <div class="display-6 fw-bold text-warning">
                                $${formatNumber(
                                    projection.next_quarter
                                )}
                            </div>

                            <p class="card-text mt-2">
                                Total projected cost for the next 3 months
                            </p>

                            <small class="text-muted">
                                Based on current monthly growth trend
                            </small>

                        </div>

                    </div>
                </div>

            </div>

        </div>
    `;
}
            // RECOMMENDATIONS
            html += `
                <div class="feature-card mb-4">
                    <div class="row align-items-center mb-4">
                        <div class="col-md-8">
                            <h3 class="fw-bold mb-0"><i class="fas fa-bullseye me-2"></i>Optimization Recommendations</h3>
                        </div>
                        <div class="col-md-4 text-end">
                            <div class="badge bg-success savings-badge">
                                <i class="fas fa-money-bill-wave me-1"></i>
                                Total Potential Savings: $${formatNumber(analysis.total_potential_savings)}/month
                            </div>
                        </div>
                    </div>
                    
                    <div id="recommendationsList"></div>
                </div>
            `;
            
            // Export Options
            html += `
                <div class="row mb-4">
                    <div class="col-md-12">
                        <div class="feature-card h-100 d-flex flex-column justify-content-center">
                            <h4 class="fw-bold mb-3 text-center"><i class="fas fa-download me-2"></i>Export Options</h4>
                            <div class="d-grid gap-2">
                                <button class="btn btn-danger btn-lg" onclick="downloadPDF()">
                                    <i class="fas fa-file-pdf me-2"></i>Download PDF Report
                                </button>
                                <button class="btn btn-outline-secondary btn-lg" onclick="resetAnalysis()">
                                    <i class="fas fa-redo me-2"></i>Analyze Another File
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('resultsContainer').innerHTML = html;
            
            // Display recommendations
            displayRecommendations(analysis.recommendations);
            
            // Generate chart if data available
            if (analysis.chart_data && analysis.chart_data.service_costs) {
                generateCostChart(analysis.chart_data.service_costs);
            }

            if (analysis.chart_data && analysis.chart_data.department_costs) {
                generateDeptCostChart(analysis.chart_data.department_costs);
            }
        }
        
        // Display recommendations list
        function displayRecommendations(recommendations) {
            let html = '';
            
            if (recommendations.length === 0) {
                html = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>No specific recommendations generated.</strong> This could be due to insufficient data or all resources being properly sized.
                    </div>
                `;
            } else {
                recommendations.forEach((rec, index) => {
                    const borderColors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0'];
                    const borderColor = borderColors[index % borderColors.length];
                    
                    html += `
                        <div class="recommendation-simple" style="border-left-color: ${borderColor}">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h5 class="fw-bold mb-1">${index + 1}. ${rec.type}</h5>
                                    <p class="mb-1"><strong>${rec.description}</strong></p>
                                    <small class="text-muted">${rec.reason}</small>
                                </div>
                                <div class="col-md-4 text-end">
                                    <div class="savings-highlight">
                                        Save $${formatNumber(rec.potential_savings)}/month
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            
            document.getElementById('recommendationsList').innerHTML = html;
        }
        
        // Generate cost distribution chart
        function generateCostChart(chartData) {
            const trace = {
                labels: chartData.labels,
                values: chartData.values,
                type: 'pie',
                hole: 0.4,
                textinfo: 'label+percent',
                hoverinfo: 'label+value+percent',
                textposition: 'outside',
                marker: {
                    colors: chartData.colors || ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                }
            };
            
            const layout = {
                title: 'Monthly Cost Distribution by Service',
                height: 400,
                showlegend: true,
                legend: {
                    orientation: 'h',
                    y: -0.1
                },
                margin: { t: 50, b: 50, l: 50, r: 50 }
            };
            
            Plotly.newPlot('costChart', [trace], layout, { displayModeBar: true });
        }

        // Generate department cost distribution chart
        function generateDeptCostChart(chartData) {
            const trace = {
                labels: chartData.labels,
                values: chartData.values,
                type: 'pie',
                hole: 0.4,
                textinfo: 'label+percent',
                hoverinfo: 'label+value+percent',
                textposition: 'outside',
                marker: {
                    colors: chartData.colors || ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#8AC926', '#1982C4']
                }
            };
            
            const layout = {
                title: 'Monthly Cost Distribution by Department',
                height: 400,
                showlegend: true,
                legend: {
                    orientation: 'h',
                    y: -0.1
                },
                margin: { t: 50, b: 50, l: 50, r: 50 }
            };
            
            Plotly.newPlot('deptCostChart', [trace], layout, { displayModeBar: true });
        }
        
        // Error display
        function showError(message) {
            document.getElementById('resultsContainer').innerHTML = `
                <div class="feature-card">
                    <div class="alert alert-danger">
                        <h4><i class="fas fa-exclamation-triangle me-2"></i>Analysis Failed</h4>
                        <p>${message}</p>
                        <p>Please check your file format and try again.</p>
                    </div>
                </div>
            `;
        }
        
        // Download PDF function
        async function downloadPDF() {
            if (!currentAnalysisData) {
                alert('No analysis data available. Please run an analysis first.');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'flex';
            
            try {
                const response = await fetch('/generate_pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ analysis: currentAnalysisData })
                });
                
                if (!response.ok) {
                    throw new Error('PDF generation failed');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'cloud_cost_analysis_report.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                
            } catch (error) {
                alert('Error generating PDF: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function resetAnalysis() {
            if (confirm('Reset current analysis and start over?')) {
                document.getElementById('fileInput').value = '';
                document.getElementById('resultsContainer').innerHTML = '';
                document.getElementById('dataQualityAlerts').innerHTML = '';
                document.getElementById('dataQualityAlerts').style.display = 'none';
                currentAnalysisData = null;
            }
        }
    </script>
</body>
</html>
'''

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        provider = request.form.get('provider', 'Auto-detect')
        
        # Validate provider
        supported_providers = ['AWS', 'Azure', 'GCP', 'Oracle', 'IBM', 'Auto-detect']
        if provider not in supported_providers:
            return jsonify({
                'success': False, 
                'error': f'Cloud provider "{provider}" is not supported. Please choose from: AWS, Azure, GCP, Oracle, IBM, or Auto-detect'
            }), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        file_extension = file.filename.lower().split('.')[-1]
        
        if file_extension == 'csv':
            df = pd.read_csv(file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type. Please upload CSV or Excel.'}), 400

	        
        print(f"📊 Data loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Perform analysis
        analysis_results = analyze_cloud_costs(df, provider)
        
        return jsonify({
            'success': True,
            'analysis': analysis_results,
            'file_info': {
                'name': file.filename,
                'size': len(df),
                'columns': list(df.columns)
            }
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        analysis_data = request.json.get('analysis')
        if not analysis_data:
            return jsonify({'success': False, 'error': 'No analysis data provided'}), 400
        
        pdf_data = generate_pdf_report(analysis_data)
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=cloud_cost_analysis_report.pdf'
        return response
        
    except Exception as e:
        print(f"❌ PDF Generation Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 PROFESSIONAL CLOUD COST OPTIMIZER - COMPLETE INTEGRATED SOLUTION")
    print("=" * 80)
    print("✨ Features Included:")
    print("   • Auto-detection for AWS, Azure, GCP, Oracle, IBM Cloud")
    print("   • Specific recommendations like 'Change from m5.xlarge to m5.large (50% savings)'")
    print("   • PDF report generation with Department Ranking")
    print("=" * 80)
    print("📁 Supported Input:")
    print("   • CSV files (Cost, ResourceName, Service, Utilization, Department, Date)")
    print("=" * 80)
    print("🌐 Starting server at: http://localhost:5000")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)