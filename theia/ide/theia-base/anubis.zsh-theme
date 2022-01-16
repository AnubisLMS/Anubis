#!/usr/bin/zsh
# FROM: https://github.com/wabscale/dots/blob/master/zsh/myscumbag.zsh-theme

export VIRTUAL_ENV_DISABLE_PROMPT=1

function virtualenv_info {
    [ $VIRTUAL_ENV ] && echo '('%F{blue}`basename $VIRTUAL_ENV`%f') '
}

setopt prompt_subst

autoload -U add-zsh-hook
autoload -Uz vcs_info

function my_git_prompt() {
  tester=$(git rev-parse --git-dir 2> /dev/null) || return

  INDEX=$(git status --porcelain 2> /dev/null)
  STATUS=""

  # is branch ahead?
  if $(echo "$(git log origin/$(git_current_branch)..HEAD 2> /dev/null)" | grep '^commit' &> /dev/null); then
    STATUS="$STATUS$ZSH_THEME_GIT_PROMPT_AHEAD"
  fi

  # is branch behind?
  if $(echo "$(git log HEAD..origin/$(git_current_branch) 2> /dev/null)" | grep '^commit' &> /dev/null); then
    STATUS="$STATUS$ZSH_THEME_GIT_PROMPT_BEHIND"
  fi

  # is anything staged?
  if $(echo "$INDEX" | command grep -E -e '^(D[ M]|[MARC][ MD]) ' &> /dev/null); then
    STATUS="$STATUS$ZSH_THEME_GIT_PROMPT_STAGED"
  fi

  # is anything unstaged?
  if $(echo "$INDEX" | command grep -E -e '^[ MARC][MD] ' &> /dev/null); then
    STATUS="$STATUS$ZSH_THEME_GIT_PROMPT_UNSTAGED"
  fi

  # is anything untracked?
  if $(echo "$INDEX" | grep '^?? ' &> /dev/null); then
    STATUS="$STATUS$ZSH_THEME_GIT_PROMPT_UNTRACKED"
  fi

  # is anything unmerged?
  if $(echo "$INDEX" | command grep -E -e '^(A[AU]|D[DU]|U[ADU]) ' &> /dev/null); then
    STATUS="$STATUS$ZSH_THEME_GIT_PROMPT_UNMERGED"
  fi

  if [[ -n $STATUS ]]; then
    STATUS=" $STATUS"
  fi

  ZSH_THEME_GIT_PROMPT_SHA_BEFORE="%{$fg_bold[magenta]%}"
  ZSH_THEME_GIT_PROMPT_SHA_AFTER="%{$reset_color%}"
  BRANCH_STATUS="$(my_current_branch)%{$reset_color%}%{$fg_bold[white]%}@%{$reset_color%}$(git_prompt_short_sha)"
  echo "$ZSH_THEME_GIT_PROMPT_PREFIX$BRANCH_STATUS$STATUS$ZSH_THEME_GIT_PROMPT_SUFFIX"
}

function my_current_branch() {
  echo $(git_current_branch || echo "(no branch)")
}

function ssh_connection() {
  if [[ -n $SSH_CONNECTION ]]; then
    echo "%{$fg_bold[red]%}(ssh) "
  fi
}

mydocker() {
    if [ -f ./docker-compose.yml ] || [ -f ./docker-compose.yaml ] || [ -f ./Dockerfile ]; then
        echo "%{$fg[blue]%} %{$reset_color%}"
    fi
}

function mygit() {
    if [[ "$(git config --get oh-my-zsh.hide-status)" != "1" ]]; then
        ref=$(command git symbolic-ref HEAD 2> /dev/null) || \
            ref=$(command git rev-parse --short HEAD 2> /dev/null) || return
        echo "$ZSH_THEME_GIT_PROMPT_PREFIX${ref#refs/heads/}$(git_prompt_short_sha)$(git_prompt_status)%{$fg_bold[blue]%}$ZSH_THEME_GIT_PROMPT_SUFFIX"
    fi
}


local ret_status="%(?:%{$fg_bold[green]%}:%{$fg_bold[red]%})%?%{$reset_color%}"
PROMPT=$'$(ssh_connection)%{$fg_bold[green]%}%n%{$reset_color%}%{$fg_bold[white]%}@%{$reset_color%}%{$fg_bold[green]%}%m%{$reset_color%}$(my_git_prompt) : %{$fg_bold[magenta]%}%~%{$reset_color%} $vcs_info_msg_0_$(virtualenv_info) $(mydocker)\n[${ret_status}] %# '

ZSH_THEME_PROMPT_RETURNCODE_PREFIX="%{$fg_bold[red]%}"
ZSH_THEME_GIT_PROMPT_PREFIX=" $fg[white]‹ %{$fg_bold[yellow]%}"
ZSH_THEME_GIT_PROMPT_AHEAD="%{$fg_bold[magenta]%}↑"
ZSH_THEME_GIT_PROMPT_BEHIND="%{$fg_bold[green]%}↓"
ZSH_THEME_GIT_PROMPT_STAGED="%{$fg_bold[green]%}●"
ZSH_THEME_GIT_PROMPT_UNSTAGED="%{$fg_bold[red]%}●"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%{$fg_bold[white]%}●"
ZSH_THEME_GIT_PROMPT_UNMERGED="%{$fg_bold[red]%}✕"
ZSH_THEME_GIT_PROMPT_SUFFIX=" $fg_bold[white]›%{$reset_color%}"