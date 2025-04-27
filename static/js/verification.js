// static/js/verification.js
document.addEventListener('DOMContentLoaded', function() {
    const verificationOptions = document.querySelectorAll('input[name="verificationMethod"]');
    const verificationArea = document.getElementById('verificationArea');
    const verifyBtn = document.getElementById('verifyBtn');
    const form = document.getElementById('loginForm') || document.getElementById('signupForm');

    let mouseData = { positions: [], timestamps: [] };
    let typingData = { keystrokeTimes: [], startTime: null };
    let isVerified = false;
    let pasteAttempts = 0;
    let mouseMoved = false; // Track if mouse has been moved

    // Initial setup
    setupVerificationMethod(document.querySelector('input[name="verificationMethod"]:checked').value);

    // Switch verification method
    verificationOptions.forEach(option => {
        option.addEventListener('change', function() {
            setupVerificationMethod(this.value);
            mouseData = { positions: [], timestamps: [] };
            typingData = { keystrokeTimes: [], startTime: null };
            isVerified = false;
            pasteAttempts = 0;
            mouseMoved = false; // Reset mouseMoved state
        });
    });

    function setupVerificationMethod(method) {
        if (method === 'captcha') {
            verificationArea.innerHTML = `
                <div class="captcha-container">
                    <div class="input-group">
                        <label for="captchaInput">Enter the text shown above:</label>
                        <img id="captchaImage" alt="CAPTCHA" class="captcha-image">
                        <input type="text" id="captchaInput" name="captchaInput" required>
                    </div>
                    <button type="button" class="captcha-refresh" id="refreshCaptcha">Refresh CAPTCHA</button>
                    <button type="button" class="btn" onclick="playAudio()">🔊 Audio</button>
                </div>
            `;
            loadCaptchaImage();
            document.getElementById('refreshCaptcha').addEventListener('click', loadCaptchaImage);
        } else if (method === 'behaviour') {
            verificationArea.innerHTML = `
                <div class="behavior-container">
                    <div class="mouse-track-area" id="mouseTrackArea">
                        <p>Move your mouse naturally within this area</p>
                    </div>
                    <div class="typing-test-container" style="display: none;">
                        <p>Type this sentence: <span id="sentenceToType"></span></p>
                        <input type="text" id="typingInput" class="typing-input" placeholder="Type the sentence here..." autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
                        <button id="verifyTypingBtn" class="btn">Complete Verify</button>
                    </div>
                </div>
            `;
            setupMouseCanvas();
            trackMouseAndTyping();
            generateNewSentence();
        }
    }

    function loadCaptchaImage() {
        fetch('/api/generate-captcha')
        .then(response => response.text())
        .then(data => {
            document.getElementById('captchaImage').src = data;
            document.getElementById('captchaInput').value = '';
            isVerified = false;
            refreshAudio();
        })
        .catch(error => {
            console.error('Error loading CAPTCHA:', error);
            alert('Failed to load CAPTCHA. Please try again.');
        });
    }

    function refreshAudio() {
        const audio = document.getElementById('captcha-audio');
        if (audio) {
            audio.src = '/audio?t=' + new Date().getTime();
            audio.load();
        }
    }

    window.playAudio = function() {
        const audio = new Audio('/audio?t=' + new Date().getTime());
        audio.play();
    };

    function setupMouseCanvas() {
        const mouseTrackArea = document.getElementById('mouseTrackArea');
        mouseTrackArea.addEventListener('mousemove', (e) => {
            const rect = mouseTrackArea.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            mouseData.positions.push([x, y]);
            mouseData.timestamps.push(Date.now());
            console.log('Mouse position:', x, y, 'Timestamp:', Date.now());
            mouseMoved = true; // Track mouse movement
        });
    }

    function trackMouseAndTyping() {
        const typingInput = document.getElementById('typingInput');
        if (!typingInput) {
            console.error('Typing input not found!');
            return;
        }
        typingInput.addEventListener('keydown', () => {
            if (!typingData.startTime) typingData.startTime = Date.now();
            const time = (Date.now() - typingData.startTime) / 1000;
            typingData.keystrokeTimes.push(time);
            console.log('Keystroke time:', time);
        });
        typingInput.addEventListener('paste', function(e) {
            e.preventDefault();
            pasteAttempts++;
            if (pasteAttempts === 1) {
                alert("Pasting is not allowed. Please type the sentence.");
            } else {
                alert("Repeated pasting detected. Closing tab.");
                window.close();
                throw new Error("Pasting detected. Tab closed.");
            }
        });
    }

    function verifyCaptcha() {
        const captchaInput = document.getElementById('captchaInput').value;
        fetch('/api/verify-captcha', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ captcha: captchaInput })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                isVerified = true;
                submitForm();
            } else {
                alert(data.message);
                loadCaptchaImage();
            }
        });
    }

    function verifyBehavior() {
        console.log('Mouse data:', mouseData);
        console.log('Typing data:', typingData);

        if (!mouseMoved) {
            alert("Please move your mouse within the tracking area before verifying.");
            return;
        }

        if (mouseData.positions.length < 10) {
            alert("Please move your mouse more within the tracking area");
            return;
        }

        // Show the typing area and generate the sentence
        document.querySelector('.typing-test-container').style.display = 'block';
        generateNewSentence();

        if (typingData.keystrokeTimes.length < 3) {
            alert("Please type the sentence in the typing area to verify");
            return;
        }

        const typingInput = document.getElementById('typingInput').value;
        const sentenceToType = document.getElementById('sentenceToType').textContent;
        if (typingInput.trim() !== sentenceToType.trim()) {
            alert("The typed sentence does not match. Please try again.");
            typingData = { keystrokeTimes: [], startTime: null };
            document.getElementById('typingInput').value = '';
            generateNewSentence();
            return;
        }

        const textLength = typingInput.length;
        const totalTime = typingData.startTime ? (Date.now() - typingData.startTime) / 1000 : 0;

        let velocities = [];
        let jerks = [];
        for (let i = 1; i < mouseData.positions.length; i++) {
            let dt = (mouseData.timestamps[i] - mouseData.timestamps[i - 1]) / 1000;
            if (dt > 0) {
                let dx = mouseData.positions[i][0] - mouseData.positions[i - 1][0];
                let dy = mouseData.positions[i][1] - mouseData.positions[i - 1][1];
                let velocity = Math.sqrt(dx * dx + dy * dy) / dt;
                velocities.push(velocity);
                if (velocities.length > 1) {
                    let jerk = (velocities[velocities.length - 1] - velocities[velocities.length - 2]) / dt;
                    jerks.push(jerk);
                }
            }
        }
        let velocityFluctuation = standardDeviation(velocities);
        let jerkFluctuation = standardDeviation(jerks);

        let keyPressIntervals = [];
        for (let i = 1; i < typingData.keystrokeTimes.length; i++) {
            keyPressIntervals.push(typingData.keystrokeTimes[i] - typingData.keystrokeTimes[i - 1]);
        }
        let keypressVariability = standardDeviation(keyPressIntervals);

        Promise.all([
            fetch('/verify-mouse-advanced', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    positions: mouseData.positions,
                    timestamps: mouseData.timestamps,
                    velocityFluctuation: velocityFluctuation,
                    jerkFluctuation: jerkFluctuation,
                }),
            }).then(res => res.json()).catch(err => {
                console.error('Mouse verification error:', err);
                return { is_human: false, reason: 'Server error' };
            }),
            fetch('/verify-typing-advanced', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    keystrokeTimes: typingData.keystrokeTimes,
                    textLength: textLength,
                    totalTime: totalTime,
                    keypressVariability: keypressVariability,
                }),
            }).then(res => res.json()).catch(err => {
                console.error('Typing verification error:', err);
                return { is_human: false, reason: 'Server error' };
            }),
        ]).then(([mouseResult, typingResult]) => {
            console.log('Mouse result:', mouseResult);
            console.log('Typing result:', typingResult);
            if (mouseResult.is_human && typingResult.is_human) {
                isVerified = true;
                alert('Behavior verified!');
                submitForm();
            } else {
                alert('Behavior verification failed: ' +
                    (mouseResult.reason || 'Mouse issue') + ' | ' +
                    (typingResult.reason || 'Typing issue'));
                mouseData = { positions: [], timestamps: [] };
                typingData = { keystrokeTimes: [], startTime: null };
                document.getElementById('typingInput').value = '';
                generateNewSentence();
            }
        });
    }

    function generateNewSentence() {
        fetch('/api/generate-sentence')
            .then(response => response.json())
            .then(data => {
                document.getElementById('sentenceToType').textContent = data.sentence;
            })
            .catch(error => console.error('Error generating sentence:', error));
    }

    function submitForm() {
        if (!isVerified) return;
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect || '/main';
            } else {
                alert(data.message);
            }
        });
    }

    verifyBtn.addEventListener('click', () => {
        const method = document.querySelector('input[name="verificationMethod"]:checked').value;
        if (method === 'captcha') {
            verifyCaptcha();
        } else {
            verifyBehavior();
        }
    });

    function standardDeviation(values) {
        if (values.length < 2) return 0;
        let avg = values.reduce((a, b) => a + b) / values.length;
        let squareDiffs = values.map(value => Math.pow(value - avg, 2));
        let avgSquareDiff = squareDiffs.reduce((a, b) => a + b) / squareDiffs.length;
        return Math.sqrt(avgSquareDiff);
    }
});