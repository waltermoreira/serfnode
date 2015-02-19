#!/bin/bash

cat <<EOF
sf() { switch=\$1;
  shift;
  img=\$1;
  shift;
  yml=\$1;
  if [[ -z "\${switch}" ]]; then
      echo "usage: serfnode run <image> <yaml>";
      return;
  fi;
  if [[ "\${switch}" != "run" ]]; then
      echo "only 'run' is supported at the moment";
      return;
  fi;
  if [[ -z "\${yml}" ]]; then
      docker run -v /:/host \${img};
  else
      yml=\$(readlink -e \$yml);
      docker run -v /:/host -v \${yml}:/serfnode.yml \${img};
  fi;
};
alias serfnode='sf';
EOF
