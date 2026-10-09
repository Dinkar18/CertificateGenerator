document.addEventListener('DOMContentLoaded', () => {
    const recipientsList = document.getElementById('recipientsList');
    const addBtn = document.getElementById('addRecipientBtn');
    const form = document.getElementById('jobForm');
    
    // UI Elements for Dashboard
    const dashboard = document.getElementById('dashboard');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const statTotal = document.getElementById('statTotal');
    const statSuccess = document.getElementById('statSuccess');
    const statFailed = document.getElementById('statFailed');
    const downloadSection = document.getElementById('downloadSection');
    const downloadList = document.getElementById('downloadList');
    const newJobBtn = document.getElementById('newJobBtn');

    let pollInterval;
    let currentJobId;

    // Add initial recipient row
    addRecipientRow();

    addBtn.addEventListener('click', addRecipientRow);

    function addRecipientRow() {
        const row = document.createElement('div');
        row.className = 'recipient-row';
        row.innerHTML = `
            <input type="text" class="recip-name" placeholder="Name (Required)" required>
            <input type="email" class="recip-email" placeholder="Email (Optional)">
            <button type="button" class="btn-remove" title="Remove">&times;</button>
        `;
        
        row.querySelector('.btn-remove').addEventListener('click', () => {
            if (recipientsList.children.length > 1) {
                row.remove();
            }
        });
        
        recipientsList.appendChild(row);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const recipients = [];
        document.querySelectorAll('.recipient-row').forEach(row => {
            const name = row.querySelector('.recip-name').value.trim();
            const email = row.querySelector('.recip-email').value.trim();
            if (name) {
                recipients.push({ name, email: email || null });
            }
        });

        const payload = {
            event_name: document.getElementById('event_name').value.trim(),
            event_date: document.getElementById('event_date').value.trim(),
            issuer_name: document.getElementById('issuer_name').value.trim(),
            recipients: recipients
        };

        try {
            const btn = document.getElementById('submitJobBtn');
            btn.disabled = true;
            btn.innerText = "Starting...";

            const res = await fetch('/api/v1/jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail?.message || "Failed to create job");
            }

            const data = await res.json();
            currentJobId = data.id;
            
            // Switch UI
            form.classList.add('hidden');
            dashboard.classList.remove('hidden');
            
            // Start Polling
            pollJobStatus();
            pollInterval = setInterval(pollJobStatus, 2000);

        } catch (error) {
            alert(error.message);
            document.getElementById('submitJobBtn').disabled = false;
            document.getElementById('submitJobBtn').innerText = "Generate Certificates";
        }
    });

    async function pollJobStatus() {
        try {
            const res = await fetch(`/api/v1/jobs/${currentJobId}`);
            if (!res.ok) return;

            const data = await res.json();
            
            // Update Dashboard
            progressBar.style.width = `${data.progress_percentage}%`;
            statusText.innerText = `Status: ${data.status.replace(/_/g, ' ')}`;
            statTotal.innerText = data.total_count;
            statSuccess.innerText = data.success_count;
            statFailed.innerText = data.failure_count;

            if (data.status === "COMPLETED" || data.status === "COMPLETED_WITH_ERRORS" || data.status === "FAILED") {
                clearInterval(pollInterval);
                fetchCertificates(data);
            }

        } catch (e) {
            console.error("Polling error", e);
        }
    }

    async function fetchCertificates(jobData) {
        downloadSection.classList.remove('hidden');
        downloadList.innerHTML = '';
        
        const zipBtn = document.getElementById('downloadZipBtn');
        if (jobData.success_count > 0) {
            zipBtn.href = `/api/v1/jobs/${currentJobId}/download-zip`;
            zipBtn.classList.remove('hidden');
        } else {
            zipBtn.classList.add('hidden');
        }

        if (!jobData.certificates || jobData.certificates.length === 0) {
            downloadList.innerHTML = `<li><span>No certificates found.</span></li>`;
            return;
        }

        jobData.certificates.forEach(cert => {
            const li = document.createElement('li');
            if (cert.status === 'SUCCESS') {
                li.innerHTML = `
                    <span>${cert.recipient_name}</span>
                    <a href="/api/v1/certificates/${cert.id}" target="_blank">Download PDF</a>
                `;
            } else {
                li.innerHTML = `
                    <span>${cert.recipient_name}</span>
                    <span style="color: var(--failed); font-size: 0.85rem;">Failed: ${cert.error_message || 'Error'}</span>
                `;
            }
            downloadList.appendChild(li);
        });
    }

    newJobBtn.addEventListener('click', () => {
        form.reset();
        recipientsList.innerHTML = '';
        addRecipientRow();
        form.classList.remove('hidden');
        dashboard.classList.add('hidden');
        downloadSection.classList.add('hidden');
        document.getElementById('submitJobBtn').disabled = false;
        document.getElementById('submitJobBtn').innerText = "Generate Certificates";
        progressBar.style.width = '0%';
    });
});
