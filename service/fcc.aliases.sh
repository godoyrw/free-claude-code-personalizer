fcc_inst() {
  echo "${SUDO_USER:-$USER}"
}

fcc_check() {
  systemctl list-unit-files | grep -q "fcc@.service" || {
    echo "fcc@.service não instalado"
    return 1
  }
}

alias fcc-start='fcc_check && sudo systemctl start fcc@$(fcc_inst)'
alias fcc-stop='fcc_check && sudo systemctl stop fcc@$(fcc_inst)'
alias fcc-restart='fcc_check && sudo systemctl restart fcc@$(fcc_inst)'
alias fcc-status='fcc_check && systemctl status fcc@$(fcc_inst)'
alias fcc-logs='journalctl -u fcc@$(fcc_inst) -f'



