#!/bin/bash

# GenX FX Laptop Connection and Verification Script
echo "🔗 Connecting to laptop shell for GenX FX verification..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
check_project_directory() {
    print_status "Checking project directory..."
    
    if [ -f "main.py" ] && [ -f "deployment_summary.json" ]; then
        print_success "✅ GenX FX project directory found"
        return 0
    else
        print_error "❌ Not in GenX FX project directory"
        print_status "Please navigate to your GenX FX project directory first"
        return 1
    fi
}

# Check Python installation
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version)
        print_success "✅ Python3 found: $python_version"
        return 0
    elif command -v python &> /dev/null; then
        python_version=$(python --version)
        print_success "✅ Python found: $python_version"
        return 0
    else
        print_error "❌ Python not found"
        print_status "Please install Python 3.7+ first"
        return 1
    fi
}

# Install required Python packages
install_dependencies() {
    print_status "Installing required Python packages..."
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        pip_cmd="pip3"
    elif command -v pip &> /dev/null; then
        pip_cmd="pip"
    else
        print_error "❌ pip not found"
        return 1
    fi
    
    # Install required packages
    print_status "Installing requests for network connectivity checks..."
    $pip_cmd install requests
    
    print_success "✅ Dependencies installed"
    return 0
}

# Run verification script
run_verification() {
    print_status "Running deployment verification..."
    
    if [ -f "verify_deployment.py" ]; then
        python3 verify_deployment.py
        return $?
    else
        print_error "❌ verify_deployment.py not found"
        return 1
    fi
}

# Show quick status
show_quick_status() {
    print_status "Quick status check..."
    
    echo ""
    echo "📁 Project Files:"
    if [ -f "main.py" ]; then echo "  ✅ main.py"; else echo "  ❌ main.py"; fi
    if [ -f "deployment_summary.json" ]; then echo "  ✅ deployment_summary.json"; else echo "  ❌ deployment_summary.json"; fi
    if [ -f "amp_auth.json" ]; then echo "  ✅ amp_auth.json"; else echo "  ❌ amp_auth.json"; fi
    
    echo ""
    echo "🔧 Tools:"
    if command -v docker &> /dev/null; then echo "  ✅ Docker"; else echo "  ❌ Docker"; fi
    if command -v railway &> /dev/null; then echo "  ✅ Railway CLI"; else echo "  ❌ Railway CLI"; fi
    if command -v gcloud &> /dev/null; then echo "  ✅ Google Cloud CLI"; else echo "  ❌ Google Cloud CLI"; fi
    if command -v vercel &> /dev/null; then echo "  ✅ Vercel CLI"; else echo "  ❌ Vercel CLI"; fi
    
    echo ""
    echo "🌐 Network:"
    if curl -s --connect-timeout 5 https://api.github.com > /dev/null; then echo "  ✅ GitHub"; else echo "  ❌ GitHub"; fi
    if curl -s --connect-timeout 5 https://railway.app > /dev/null; then echo "  ✅ Railway"; else echo "  ❌ Railway"; fi
    if curl -s --connect-timeout 5 https://supabase.com > /dev/null; then echo "  ✅ Supabase"; else echo "  ❌ Supabase"; fi
}

# Main function
main() {
    echo "🚀 GenX FX Laptop Verification"
    echo "=============================="
    
    # Check project directory
    if ! check_project_directory; then
        exit 1
    fi
    
    # Check Python
    if ! check_python; then
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Show quick status
    show_quick_status
    
    echo ""
    print_status "Choose an option:"
    echo "1. Run full verification (recommended)"
    echo "2. Quick status check only"
    echo "3. Exit"
    
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            run_verification
            ;;
        2)
            print_success "Quick status check completed above"
            ;;
        3)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    print_status "Verification completed!"
    print_status "Check verification_report.json for detailed results"
}

# Run main function
main "$@"