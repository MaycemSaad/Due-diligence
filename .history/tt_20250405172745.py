elif page == "about":
    st.markdown("""
        <div style="padding: 4rem 2rem; background: #f4f4f4; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center;">
            <h2 style="color: #333; font-size: 2.5rem; font-weight: bold;">About Us</h2>
            <p style="font-size: 1.2rem; color: #555; max-width: 800px; margin: auto;">
                We are a team of passionate professionals dedicated to transforming the due diligence process.
                Our platform combines cutting-edge technology, AI, and decades of experience to help investors,
                startups, and enterprises make more informed decisions, faster.
            </p>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 3rem;">
                <div style="width: 250px; padding: 2rem; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin: 10px;">
                    <h3 style="color: #06f; font-size: 1.8rem; font-weight: bold;">Our Mission</h3>
                    <p style="font-size: 1.1rem; color: #777;">
                        Our mission is to simplify the due diligence process for everyone. We believe in empowering
                        our clients to make informed, confident decisions by automating key processes and offering
                        real-time insights.
                    </p>
                </div>
                <div style="width: 250px; padding: 2rem; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin: 10px;">
                    <h3 style="color: #06f; font-size: 1.8rem; font-weight: bold;">Our Vision</h3>
                    <p style="font-size: 1.1rem; color: #777;">
                        We aim to revolutionize due diligence by combining innovation, data security, and AI-driven
                        analytics to offer unmatched accuracy and speed in the decision-making process.
                    </p>
                </div>
                <div style="width: 250px; padding: 2rem; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin: 10px;">
                    <h3 style="color: #06f; font-size: 1.8rem; font-weight: bold;">Our Values</h3>
                    <ul style="font-size: 1.1rem; color: #777; list-style-type: none; padding-left: 0;">
                        <li><i style="color: #06f; font-size: 1.2rem;">✔</i> Integrity</li>
                        <li><i style="color: #06f; font-size: 1.2rem;">✔</i> Innovation</li>
                        <li><i style="color: #06f; font-size: 1.2rem;">✔</i> Security</li>
                        <li><i style="color: #06f; font-size: 1.2rem;">✔</i> Efficiency</li>
                    </ul>
                </div>
            </div>
        </div>

        <div style="background: #06f; color: white; padding: 3rem 2rem; text-align: center; margin-top: 5rem; border-radius: 15px;">
            <h2 style="font-size: 2.5rem;">Meet The Team</h2>
            <p style="font-size: 1.1rem;">Our team of experienced professionals is dedicated to delivering top-notch service and cutting-edge solutions to our clients. Together, we bring decades of expertise to the table, ensuring that every decision made is informed, accurate, and secure.</p>
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 2rem;">
                <div style="width: 200px; text-align: center;">
                    <img src="https://via.placeholder.com/150" style="width: 150px; height: 150px; border-radius: 50%; margin-bottom: 1rem;" alt="Team Member">
                    <h3>John Doe</h3>
                    <p>CEO & Founder</p>
                </div>
                <div style="width: 200px; text-align: center;">
                    <img src="https://via.placeholder.com/150" style="width: 150px; height: 150px; border-radius: 50%; margin-bottom: 1rem;" alt="Team Member">
                    <h3>Jane Smith</h3>
                    <p>COO & Operations Lead</p>
                </div>
                <div style="width: 200px; text-align: center;">
                    <img src="https://via.placeholder.com/150" style="width: 150px; height: 150px; border-radius: 50%; margin-bottom: 1rem;" alt="Team Member">
                    <h3>Robert Brown</h3>
                    <p>CTO & Technical Lead</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
