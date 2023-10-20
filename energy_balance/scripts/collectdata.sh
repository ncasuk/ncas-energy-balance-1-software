#!/bin/bash
export PATH="/scratch/ammss-user/ncas-energy-balance-1-software/venv/bin:$PATH"
export CONFIG='/home/ammss-user/ncas-energy-balance-1-software/config.ini'
/home/ammss-user/ncas-energy-balance-1-software/venv/bin/python /home/ammss-user/ncas-energy-balance-1-software/energy_balance/scripts/download_data.py
