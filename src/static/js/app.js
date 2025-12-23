/**
 * MCE Cluster Generator - Frontend Application
 */

const API_BASE = '/api/v1';

// DOM Elements
const elements = {
    form: null,
    flavorSelect: null,
    vendorConfigsList: null,
    addVendorBtn: null,
    vendorConfigTemplate: null,
    ocpVersion: null,
    dnsDomain: null,
    outputPlaceholder: null,
    outputContent: null,
    outputError: null,
    yamlOutput: null,
    errorMessage: null,
    copyBtn: null,
    downloadBtn: null,
    resetBtn: null,
    loadingOverlay: null,
    generationInfo: null,
    infoClusterName: null,
    infoVendors: null,
    infoNodepools: null,
    infoVersion: null
};

// State
let defaults = null;
let flavors = null;
let generatedYaml = null;
let currentClusterName = null;
let vendorConfigIndex = 0;

/**
 * Initialize the application
 */
async function init() {
    try {
        // Cache DOM elements
        elements.form = document.getElementById('clusterForm');
        elements.flavorSelect = document.getElementById('flavorSelect');
        elements.vendorConfigsList = document.getElementById('vendorConfigsList');
        elements.addVendorBtn = document.getElementById('addVendorBtn');
        elements.vendorConfigTemplate = document.getElementById('vendorConfigTemplate');
        elements.ocpVersion = document.getElementById('ocpVersion');
        elements.dnsDomain = document.getElementById('dnsDomain');
        elements.outputPlaceholder = document.getElementById('outputPlaceholder');
        elements.outputContent = document.getElementById('outputContent');
        elements.outputError = document.getElementById('outputError');
        elements.yamlOutput = document.getElementById('yamlOutput');
        elements.errorMessage = document.getElementById('errorMessage');
        elements.copyBtn = document.getElementById('copyBtn');
        elements.downloadBtn = document.getElementById('downloadBtn');
        elements.resetBtn = document.getElementById('resetBtn');
        elements.loadingOverlay = document.getElementById('loadingOverlay');
        elements.generationInfo = document.getElementById('generationInfo');
        elements.infoClusterName = document.getElementById('infoClusterName');
        elements.infoVendors = document.getElementById('infoVendors');
        elements.infoNodepools = document.getElementById('infoNodepools');
        elements.infoVersion = document.getElementById('infoVersion');

        // Load defaults from API
        await loadDefaults();

        // Setup event listeners
        setupEventListeners();

        // Add initial vendor config
        addVendorConfig();
        
        console.log('MCE Cluster Generator initialized successfully');
    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
}

/**
 * Load default values from the API
 */
async function loadDefaults() {
    try {
        // Load defaults, flavors, and sites in parallel
        const [defaultsResponse, flavorsResponse, sitesResponse] = await Promise.all([
            fetch(`${API_BASE}/clusters/defaults`),
            fetch(`${API_BASE}/clusters/flavors`),
            fetch(`${API_BASE}/clusters/sites`)
        ]);

        if (!defaultsResponse.ok) {
            throw new Error('Failed to load defaults');
        }
        defaults = await defaultsResponse.json();

        if (flavorsResponse.ok) {
            const flavorsData = await flavorsResponse.json();
            flavors = flavorsData.flavors;
            populateFlavors(flavors);
        }

        if (sitesResponse.ok) {
            const sitesData = await sitesResponse.json();
            populateSites(sitesData.sites);
        }

        // Populate versions dropdown
        populateVersions(defaults.versions);

        // Set default DNS domain
        elements.dnsDomain.value = defaults.default_dns_domain;
        elements.dnsDomain.placeholder = defaults.default_dns_domain;

    } catch (error) {
        console.error('Error loading defaults:', error);
        showError('Failed to load configuration defaults. Please refresh the page.');
    }
}

/**
 * Populate flavors dropdown
 */
function populateFlavors(flavorsList) {
    if (!elements.flavorSelect || !flavorsList) return;

    elements.flavorSelect.innerHTML = `
        <option value="">-- Select a flavor or configure manually --</option>
        ${flavorsList.map(flavor => `
            <option value="${flavor.name}">${flavor.description}</option>
        `).join('')}
    `;
}

/**
 * Populate OpenShift version dropdown
 */
function populateVersions(versions) {
    elements.ocpVersion.innerHTML = versions.map(version => `
        <option value="${version.version}" ${version.is_default ? 'selected' : ''}>
            OpenShift ${version.version}${version.is_default ? ' (default)' : ''}
        </option>
    `).join('');
}

/**
 * Populate sites dropdown
 */
function populateSites(sites) {
    const siteSelect = document.getElementById('site');
    if (!siteSelect || !sites) return;

    siteSelect.innerHTML = `
        <option value="">-- Select a site --</option>
        ${sites.map(site => `
            <option value="${site}">${site}</option>
        `).join('')}
    `;
}

/**
 * Add a new vendor configuration card
 */
function addVendorConfig(preselectedVendor = null) {
    if (!defaults) return;
    
    const template = elements.vendorConfigTemplate.content.cloneNode(true);
    const card = template.querySelector('.vendor-config-card');
    card.dataset.index = vendorConfigIndex++;
    
    // Populate vendor dropdown
    const vendorSelect = card.querySelector('.vendor-select');
    vendorSelect.innerHTML = `
        <option value="">Select vendor...</option>
        ${defaults.vendors.map(v => `
            <option value="${v.name}" ${v.name === preselectedVendor ? 'selected' : ''}>
                ${v.display_name}
            </option>
        `).join('')}
    `;
    
    // Add remove button handler
    const removeBtn = card.querySelector('.btn-remove-vendor');
    removeBtn.addEventListener('click', () => {
        card.remove();
        updateRemoveButtons();
    });
    
    elements.vendorConfigsList.appendChild(card);
    updateRemoveButtons();
}

/**
 * Update remove buttons visibility (hide if only one vendor)
 */
function updateRemoveButtons() {
    const cards = elements.vendorConfigsList.querySelectorAll('.vendor-config-card');
    cards.forEach(card => {
        const removeBtn = card.querySelector('.btn-remove-vendor');
        removeBtn.style.display = cards.length > 1 ? 'flex' : 'none';
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Form submission
    elements.form.addEventListener('submit', handleFormSubmit);

    // Flavor selection
    if (elements.flavorSelect) {
        elements.flavorSelect.addEventListener('change', handleFlavorChange);
    }

    // Add vendor button
    elements.addVendorBtn.addEventListener('click', () => addVendorConfig());

    // Reset button
    elements.resetBtn.addEventListener('click', handleReset);

    // Copy button
    elements.copyBtn.addEventListener('click', handleCopy);

    // Download button
    elements.downloadBtn.addEventListener('click', handleDownload);

    // Max pods radio buttons
    const maxPodsGroup = document.getElementById('maxPodsGroup');
    maxPodsGroup.querySelectorAll('.radio-label').forEach(label => {
        label.addEventListener('click', (e) => {
            // Update selected state
            maxPodsGroup.querySelectorAll('.radio-label').forEach(l => l.classList.remove('selected'));
            label.classList.add('selected');
            label.querySelector('input').checked = true;
            
            // Handle var-lib-containers requirement for 500 pods
            handleMaxPodsChange(label.dataset.value);
        });
    });

    // Real-time validation feedback
    elements.form.querySelectorAll('input[required]').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearFieldError(input));
    });
}

/**
 * Handle flavor selection
 */
async function handleFlavorChange(e) {
    const flavorName = e.target.value;
    if (!flavorName) return;

    try {
        // Fetch flavor details
        const response = await fetch(`${API_BASE}/clusters/flavors/${flavorName}`);
        if (!response.ok) {
            throw new Error('Failed to load flavor');
        }
        const flavor = await response.json();
        console.log('Loaded flavor:', flavor);

        // Apply flavor to form
        applyFlavor(flavor);

    } catch (error) {
        console.error('Error loading flavor:', error);
        alert('Failed to load flavor: ' + error.message);
    }
}

/**
 * Apply flavor values to the form
 */
function applyFlavor(flavor) {
    try {
        // Clear existing vendor configs
        elements.vendorConfigsList.innerHTML = '';
        vendorConfigIndex = 0;

        // Add vendor configs from flavor
        if (flavor.vendors && flavor.vendors.length > 0) {
            flavor.vendors.forEach(vendor => {
                addVendorConfigWithValues(vendor.vendor, vendor.nodes, `${vendor.vendor}-infra`);
            });
        }

        // Set OCP version
        if (flavor.ocp_version && elements.ocpVersion) {
            elements.ocpVersion.value = flavor.ocp_version;
        }

        // Set max pods
        const maxPodsValue = (flavor.max_pods || 250).toString();
        const maxPodsGroup = document.getElementById('maxPodsGroup');
        if (maxPodsGroup) {
            maxPodsGroup.querySelectorAll('.radio-label').forEach(label => {
                label.classList.remove('selected');
                if (label.dataset.value === maxPodsValue) {
                    label.classList.add('selected');
                    label.querySelector('input').checked = true;
                }
            });
            handleMaxPodsChange(maxPodsValue);
        }

        // Set optional configs
        const varLibCheckbox = document.getElementById('varLibContainers');
        const ringsizeCheckbox = document.getElementById('ringsize');
        if (varLibCheckbox) varLibCheckbox.checked = flavor.includes_var_lib_containers || false;
        if (ringsizeCheckbox) ringsizeCheckbox.checked = flavor.includes_ringsize || false;

        // Set custom configs
        const customConfigsEl = document.getElementById('customConfigs');
        if (customConfigsEl) {
            if (flavor.custom_configs && flavor.custom_configs.length > 0) {
                customConfigsEl.value = flavor.custom_configs.join('\n');
            } else {
                customConfigsEl.value = '';
            }
        }

        // Show feedback
        showFlavorAppliedFeedback(flavor.name);
        console.log('Flavor applied successfully:', flavor.name);
    } catch (error) {
        console.error('Error applying flavor:', error);
    }
}

/**
 * Add vendor config with flavor values
 */
function addVendorConfigWithValues(vendorName, nodeCount, infraEnv) {
    if (!defaults) return;
    
    const template = elements.vendorConfigTemplate.content.cloneNode(true);
    const card = template.querySelector('.vendor-config-card');
    card.dataset.index = vendorConfigIndex++;
    
    // Populate vendor dropdown and select the vendor
    const vendorSelect = card.querySelector('.vendor-select');
    vendorSelect.innerHTML = `
        <option value="">Select vendor...</option>
        ${defaults.vendors.map(v => `
            <option value="${v.name}" ${v.name === vendorName ? 'selected' : ''}>
                ${v.display_name}
            </option>
        `).join('')}
    `;

    // Set node count and infra env
    card.querySelector('[name="number_of_nodes"]').value = nodeCount;
    card.querySelector('[name="infra_env_name"]').value = infraEnv;
    
    // Add remove button handler
    const removeBtn = card.querySelector('.btn-remove-vendor');
    removeBtn.addEventListener('click', () => {
        card.remove();
        updateRemoveButtons();
    });
    
    elements.vendorConfigsList.appendChild(card);
    updateRemoveButtons();
}

/**
 * Show feedback when flavor is applied
 */
function showFlavorAppliedFeedback(flavorName) {
    const select = elements.flavorSelect;
    const originalBg = select.style.backgroundColor;

    select.style.backgroundColor = 'rgba(35, 134, 54, 0.3)';
    select.style.borderColor = 'var(--color-success)';

    setTimeout(() => {
        select.style.backgroundColor = '';
        select.style.borderColor = '';
    }, 1500);
}

/**
 * Handle max pods selection change
 */
function handleMaxPodsChange(value) {
    const varLibCheckbox = document.getElementById('varLibContainers');
    const varLibLabel = varLibCheckbox.closest('.checkbox-label');
    
    if (value === '500') {
        // Force enable and disable the checkbox
        varLibCheckbox.checked = true;
        varLibCheckbox.disabled = true;
        varLibLabel.classList.add('forced');
        varLibLabel.title = 'Required for 500 pods configuration';
    } else {
        // Re-enable the checkbox
        varLibCheckbox.disabled = false;
        varLibLabel.classList.remove('forced');
        varLibLabel.title = '';
    }
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
        return;
    }

    // Get form data
    const formData = getFormData();
    
    // Show loading state
    showLoading(true);
    hideOutput();

    try {
        const response = await fetch(`${API_BASE}/clusters/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate configuration');
        }

        // Store generated YAML
        generatedYaml = data.yaml_content;
        currentClusterName = data.cluster_name;

        // Show output
        showOutput(data);

    } catch (error) {
        console.error('Error generating cluster:', error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Get form data as object
 */
function getFormData() {
    const form = elements.form;
    
    // Get vendor configurations
    const vendorConfigs = [];
    const cards = elements.vendorConfigsList.querySelectorAll('.vendor-config-card');
    
    cards.forEach(card => {
        const vendor = card.querySelector('[name="vendor"]').value;
        const numberOfNodes = parseInt(card.querySelector('[name="number_of_nodes"]').value, 10);
        const infraEnvName = card.querySelector('[name="infra_env_name"]').value.trim();
        
        if (vendor && numberOfNodes && infraEnvName) {
            vendorConfigs.push({
                vendor: vendor,
                number_of_nodes: numberOfNodes,
                infra_env_name: infraEnvName
            });
        }
    });

    // Get custom configs (split by newlines)
    const customConfigsText = form.querySelector('#customConfigs').value;
    const customConfigs = customConfigsText
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);

    // Get max pods value
    const maxPodsInput = form.querySelector('input[name="max_pods"]:checked');
    const maxPods = maxPodsInput ? parseInt(maxPodsInput.value, 10) : 250;

    return {
        cluster_name: form.querySelector('#clusterName').value.trim(),
        site: form.querySelector('#site').value.trim(),
        vendor_configs: vendorConfigs,
        ocp_version: form.querySelector('#ocpVersion').value,
        dns_domain: form.querySelector('#dnsDomain').value.trim() || defaults.default_dns_domain,
        max_pods: maxPods,
        include_var_lib_containers: form.querySelector('#varLibContainers').checked,
        include_ringsize: form.querySelector('#ringsize').checked,
        custom_configs: customConfigs
    };
}

/**
 * Validate the entire form
 */
function validateForm() {
    let isValid = true;

    // Check required fields
    elements.form.querySelectorAll('#clusterName, #site').forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    // Check vendor configurations
    const cards = elements.vendorConfigsList.querySelectorAll('.vendor-config-card');
    let hasValidVendor = false;
    
    cards.forEach(card => {
        const vendorSelect = card.querySelector('[name="vendor"]');
        const nodesInput = card.querySelector('[name="number_of_nodes"]');
        const infraEnvInput = card.querySelector('[name="infra_env_name"]');
        
        if (vendorSelect.value && nodesInput.value && infraEnvInput.value.trim()) {
            hasValidVendor = true;
        } else if (vendorSelect.value || nodesInput.value || infraEnvInput.value.trim()) {
            // Partial fill - show errors
            if (!vendorSelect.value) showFieldError(vendorSelect, 'Required');
            if (!nodesInput.value) showFieldError(nodesInput, 'Required');
            if (!infraEnvInput.value.trim()) showFieldError(infraEnvInput, 'Required');
            isValid = false;
        }
    });

    if (!hasValidVendor) {
        showError('Please add at least one vendor configuration');
        isValid = false;
    }

    return isValid;
}

/**
 * Validate a single field
 */
function validateField(input) {
    const value = input.value.trim();
    
    if (input.required && !value) {
        showFieldError(input, 'This field is required');
        return false;
    }

    if (input.pattern && value) {
        const regex = new RegExp(input.pattern);
        if (!regex.test(value)) {
            showFieldError(input, 'Invalid format');
            return false;
        }
    }

    clearFieldError(input);
    return true;
}

/**
 * Show error for a field
 */
function showFieldError(element, message) {
    element.style.borderColor = 'var(--color-error)';
}

/**
 * Clear error for a field
 */
function clearFieldError(element) {
    element.style.borderColor = '';
}

/**
 * Show the generated output
 */
function showOutput(data) {
    elements.outputPlaceholder.style.display = 'none';
    elements.outputError.style.display = 'none';
    elements.outputContent.style.display = 'block';
    elements.generationInfo.style.display = 'grid';

    // Display YAML content
    elements.yamlOutput.innerHTML = formatYamlForDisplay(data.yaml_content);

    // Enable buttons
    elements.copyBtn.disabled = false;
    elements.downloadBtn.disabled = false;

    // Update info
    elements.infoClusterName.textContent = data.cluster_name;
    elements.infoVendors.textContent = data.vendors_used.join(', ');
    elements.infoNodepools.textContent = data.nodepool_count;
    elements.infoVersion.textContent = data.ocp_version;
}

/**
 * Hide output section
 */
function hideOutput() {
    elements.outputPlaceholder.style.display = 'flex';
    elements.outputContent.style.display = 'none';
    elements.outputError.style.display = 'none';
    elements.generationInfo.style.display = 'none';
    elements.copyBtn.disabled = true;
    elements.downloadBtn.disabled = true;
}

/**
 * Show error message
 */
function showError(message) {
    elements.outputPlaceholder.style.display = 'none';
    elements.outputContent.style.display = 'none';
    elements.outputError.style.display = 'flex';
    elements.generationInfo.style.display = 'none';
    elements.errorMessage.textContent = message;
    elements.copyBtn.disabled = true;
    elements.downloadBtn.disabled = true;
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

/**
 * Handle copy to clipboard
 */
async function handleCopy() {
    if (!generatedYaml) return;

    try {
        await navigator.clipboard.writeText(generatedYaml);
        
        // Show success state
        const copyIcon = elements.copyBtn.querySelector('.copy-icon');
        const copiedIcon = elements.copyBtn.querySelector('.copied-icon');
        
        copyIcon.style.display = 'none';
        copiedIcon.style.display = 'inline';
        elements.copyBtn.classList.add('copied');

        // Reset after 2 seconds
        setTimeout(() => {
            copyIcon.style.display = 'inline';
            copiedIcon.style.display = 'none';
            elements.copyBtn.classList.remove('copied');
        }, 2000);

    } catch (error) {
        console.error('Failed to copy:', error);
        fallbackCopy(generatedYaml);
    }
}

/**
 * Fallback copy method for older browsers
 */
function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('Fallback copy failed:', err);
    }
    
    document.body.removeChild(textArea);
}

/**
 * Handle download YAML file
 */
function handleDownload() {
    if (!generatedYaml || !currentClusterName) return;

    const blob = new Blob([generatedYaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ocp4-${currentClusterName}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Handle form reset
 */
function handleReset() {
    elements.form.reset();

    // Reset flavor selector
    if (elements.flavorSelect) {
        elements.flavorSelect.value = '';
    }
    
    // Clear vendor configs and add one empty one
    elements.vendorConfigsList.innerHTML = '';
    vendorConfigIndex = 0;
    addVendorConfig();

    // Reset DNS domain to default
    if (defaults) {
        elements.dnsDomain.value = defaults.default_dns_domain;
    }

    // Reset max pods to 250
    const maxPodsGroup = document.getElementById('maxPodsGroup');
    maxPodsGroup.querySelectorAll('.radio-label').forEach(label => {
        label.classList.remove('selected');
        if (label.dataset.value === '250') {
            label.classList.add('selected');
            label.querySelector('input').checked = true;
        }
    });
    handleMaxPodsChange('250');

    // Hide output
    hideOutput();
    generatedYaml = null;
    currentClusterName = null;
}

/**
 * Escape HTML and format YAML for display
 */
function formatYamlForDisplay(yaml) {
    const escaped = yaml
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    return escaped;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
