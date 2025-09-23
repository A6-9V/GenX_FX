#!/bin/bash

# GenX Trading System - GitLab SSH Key Setup Script
# This script generates SSH keys for GitLab authentication

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔑 GenX Trading System - GitLab SSH Key Setup${NC}"
echo "=============================================="

# Get user information
echo -e "${YELLOW}📝 Setting up SSH keys for GitLab...${NC}"
echo ""

# Prompt for email (GitLab account email)
read -p "Enter your GitLab email address: " GITLAB_EMAIL

if [ -z "$GITLAB_EMAIL" ]; then
    echo -e "${RED}❌ Error: Email address is required${NC}"
    exit 1
fi

# SSH key file names
SSH_KEY_NAME="gitlab_genx_key"
SSH_DIR="$HOME/.ssh"
PRIVATE_KEY="$SSH_DIR/$SSH_KEY_NAME"
PUBLIC_KEY="$SSH_DIR/${SSH_KEY_NAME}.pub"

# Create .ssh directory if it doesn't exist
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

echo -e "${BLUE}🔧 Generating SSH key pair...${NC}"

# Generate SSH key pair
ssh-keygen -t ed25519 -C "$GITLAB_EMAIL" -f "$PRIVATE_KEY" -N ""

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSH key pair generated successfully!${NC}"
else
    echo -e "${RED}❌ Failed to generate SSH key pair${NC}"
    exit 1
fi

# Set proper permissions
chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"

echo ""
echo -e "${BLUE}📋 SSH Key Information:${NC}"
echo "  Private key: $PRIVATE_KEY"
echo "  Public key:  $PUBLIC_KEY"
echo ""

# Display the public key
echo -e "${GREEN}🔑 Your GitLab SSH Public Key:${NC}"
echo "=================================================="
cat "$PUBLIC_KEY"
echo "=================================================="
echo ""

# Copy to clipboard if possible
if command -v pbcopy >/dev/null 2>&1; then
    cat "$PUBLIC_KEY" | pbcopy
    echo -e "${GREEN}✅ Public key copied to clipboard (macOS)${NC}"
elif command -v xclip >/dev/null 2>&1; then
    cat "$PUBLIC_KEY" | xclip -selection clipboard
    echo -e "${GREEN}✅ Public key copied to clipboard (Linux)${NC}"
elif command -v clip >/dev/null 2>&1; then
    cat "$PUBLIC_KEY" | clip
    echo -e "${GREEN}✅ Public key copied to clipboard (Windows)${NC}"
else
    echo -e "${YELLOW}📋 Copy the key above manually${NC}"
fi

echo ""
echo -e "${BLUE}📝 Setup Instructions for GitLab:${NC}"
echo ""
echo "1. 🌐 Go to GitLab.com and log in to your account"
echo "2. 👤 Click on your profile picture (top right)"
echo "3. ⚙️  Select 'Preferences' from the dropdown"
echo "4. 🔑 Click on 'SSH Keys' in the left sidebar"
echo "5. 📝 Paste the public key above into the 'Key' field"
echo "6. 🏷️  Add a title like 'GenX Trading System - $(hostname)'"
echo "7. 📅 Set expiration date (optional, recommended: 1 year)"
echo "8. ✅ Click 'Add key'"
echo ""

# Create SSH config for GitLab
SSH_CONFIG="$SSH_DIR/config"
echo -e "${YELLOW}🔧 Creating SSH config for GitLab...${NC}"

# Check if config exists and backup
if [ -f "$SSH_CONFIG" ]; then
    cp "$SSH_CONFIG" "${SSH_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}📋 Backed up existing SSH config${NC}"
fi

# Add GitLab configuration
if ! grep -q "Host gitlab.com" "$SSH_CONFIG" 2>/dev/null; then
    cat >> "$SSH_CONFIG" << EOF

# GitLab configuration for GenX Trading System
Host gitlab.com
    HostName gitlab.com
    User git
    IdentityFile $PRIVATE_KEY
    IdentitiesOnly yes
    AddKeysToAgent yes

EOF
    echo -e "${GREEN}✅ GitLab SSH config added${NC}"
else
    echo -e "${YELLOW}⚠️  GitLab config already exists in SSH config${NC}"
fi

chmod 600 "$SSH_CONFIG"

echo ""
echo -e "${BLUE}🧪 Testing SSH Connection:${NC}"
echo "After adding the key to GitLab, test with:"
echo ""
echo -e "${GREEN}ssh -T git@gitlab.com${NC}"
echo ""
echo "You should see a message like:"
echo "'Welcome to GitLab, @yourusername!'"
echo ""

echo -e "${BLUE}🚀 GitLab Repository Setup:${NC}"
echo ""
echo "To use this SSH key with your GenX repository:"
echo ""
echo "1. 📂 Create a new repository on GitLab or use existing one"
echo "2. 🔗 Use the SSH clone URL (starts with git@gitlab.com:)"
echo "3. 📦 Clone your repository:"
echo -e "${GREEN}   git clone git@gitlab.com:yourusername/genx-trading-system.git${NC}"
echo ""
echo "4. 🔧 Or add GitLab as remote to existing repository:"
echo -e "${GREEN}   git remote add gitlab git@gitlab.com:yourusername/genx-trading-system.git${NC}"
echo ""

echo -e "${BLUE}🔒 Security Notes:${NC}"
echo "• Keep your private key ($PRIVATE_KEY) secure"
echo "• Never share your private key with anyone"
echo "• The public key is safe to share and goes on GitLab"
echo "• Consider setting an expiration date for the key"
echo ""

echo -e "${GREEN}🎉 SSH key setup complete!${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "1. Add the public key to your GitLab account (instructions above)"
echo "2. Test the connection: ssh -T git@gitlab.com"
echo "3. Start using GitLab with SSH authentication"