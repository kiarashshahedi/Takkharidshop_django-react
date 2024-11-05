// src/components/SellerProfile.js
import React, { useEffect, useState } from 'react';
import { getProfile } from '../api';

const SellerProfile = () => {
    const [profile, setProfile] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            const userType = "seller";
            try {
                const data = await getProfile(userType);
                setProfile(data);
            } catch (error) {
                console.error("Failed to load profile:", error);
            }
        };
        fetchProfile();
    }, []);

    if (!profile) return <div>Loading...</div>;

    return (
        <div>
            <h1>Seller Profile</h1>
            <p>Username: {profile.username}</p>
            <p>Email: {profile.email}</p>
            {/* Display other seller-specific info */}
        </div>
    );
};

export default SellerProfile;
