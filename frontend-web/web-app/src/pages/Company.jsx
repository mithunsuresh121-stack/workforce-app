import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  ArrowLeftIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  GlobeAltIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

const Company = () => {
  const { user } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCompanyData = async () => {
      if (!user?.company_id) {
        setError('No company assigned');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/api/companies/${user.company_id}`, {
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch company data');
        }

        const companyData = await response.json();
        setCompany(companyData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanyData();
  }, [user?.company_id]);

  if (loading) {
    return (
      <div className="space-y-8">
        {/* Header Section */}
        <div className="bg-surface border-b border-border">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="h-8 bg-neutral-200 rounded w-48 animate-pulse mb-2"></div>
                <div className="h-4 bg-neutral-200 rounded w-64 animate-pulse"></div>
              </div>
              <div className="h-10 bg-neutral-200 rounded-lg w-32 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6">
          <div className="bg-surface border border-border rounded-lg p-8">
            <div className="animate-pulse">
              <div className="flex items-center gap-6 mb-8">
                <div className="w-20 h-20 bg-neutral-200 rounded-lg"></div>
                <div className="space-y-3">
                  <div className="h-8 bg-neutral-200 rounded w-64"></div>
                  <div className="h-4 bg-neutral-200 rounded w-48"></div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <div className="h-6 bg-neutral-200 rounded w-40"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-neutral-200 rounded w-full"></div>
                    <div className="h-4 bg-neutral-200 rounded w-3/4"></div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="h-6 bg-neutral-200 rounded w-32"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-neutral-200 rounded w-full"></div>
                    <div className="h-4 bg-neutral-200 rounded w-5/6"></div>
                    <div className="h-4 bg-neutral-200 rounded w-4/5"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        {/* Header Section */}
        <div className="bg-surface border-b border-border">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-semibold text-neutral-900">Company Information</h1>
                <p className="text-neutral-600 mt-1">View your company details and information</p>
              </div>
              <Link
                to="/dashboard"
                className="inline-flex items-center px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
              >
                <ArrowLeftIcon className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6">
          <div className="bg-surface border border-border rounded-lg p-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <XMarkIcon className="w-8 h-8 text-danger-600" />
              </div>
              <h2 className="text-xl font-semibold text-neutral-900 mb-2">Unable to Load Company Information</h2>
              <p className="text-neutral-600 mb-6">{error}</p>
              <Link
                to="/dashboard"
                className="inline-flex items-center px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 font-medium"
              >
                <ArrowLeftIcon className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-surface border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-neutral-900">Company Information</h1>
              <p className="text-neutral-600 mt-1">View your company details and information</p>
            </div>
            <Link
              to="/dashboard"
              className="inline-flex items-center px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
            >
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6">
        <div className="bg-surface border border-border rounded-lg p-8">
          {company ? (
            <div className="space-y-8">
              {/* Company Logo and Name */}
              <div className="flex items-start gap-6">
                <div className="w-20 h-20 bg-neutral-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  {company.logo_url ? (
                    <img
                      src={company.logo_url}
                      alt={company.name}
                      className="w-20 h-20 rounded-lg object-cover"
                    />
                  ) : (
                    <BuildingOfficeIcon className="w-10 h-10 text-neutral-400" />
                  )}
                </div>
                <div className="flex-1">
                  <h2 className="text-3xl font-semibold text-neutral-900 mb-2">{company.name}</h2>
                  {company.domain && (
                    <div className="flex items-center gap-2 text-neutral-600">
                      <GlobeAltIcon className="w-4 h-4" />
                      <span>{company.domain}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Company Details */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900 mb-4">Contact Information</h3>
                    <div className="space-y-4">
                      {company.contact_email && (
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-neutral-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <EnvelopeIcon className="w-5 h-5 text-neutral-400" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-neutral-500">Email</p>
                            <p className="text-neutral-900">{company.contact_email}</p>
                          </div>
                        </div>
                      )}
                      {company.contact_phone && (
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-neutral-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <PhoneIcon className="w-5 h-5 text-neutral-400" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-neutral-500">Phone</p>
                            <p className="text-neutral-900">{company.contact_phone}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900 mb-4">Address</h3>
                    <div className="space-y-4">
                      {company.address && (
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-neutral-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                            <MapPinIcon className="w-5 h-5 text-neutral-400" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-neutral-500">Street Address</p>
                            <p className="text-neutral-900">{company.address}</p>
                          </div>
                        </div>
                      )}
                      <div className="grid grid-cols-2 gap-4">
                        {company.city && (
                          <div>
                            <p className="text-sm font-medium text-neutral-500">City</p>
                            <p className="text-neutral-900">{company.city}</p>
                          </div>
                        )}
                        {company.state && (
                          <div>
                            <p className="text-sm font-medium text-neutral-500">State</p>
                            <p className="text-neutral-900">{company.state}</p>
                          </div>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        {company.country && (
                          <div>
                            <p className="text-sm font-medium text-neutral-500">Country</p>
                            <p className="text-neutral-900">{company.country}</p>
                          </div>
                        )}
                        {company.postal_code && (
                          <div>
                            <p className="text-sm font-medium text-neutral-500">Postal Code</p>
                            <p className="text-neutral-900">{company.postal_code}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BuildingOfficeIcon className="w-8 h-8 text-neutral-400" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">No company data available</h3>
              <p className="text-neutral-600">Company information is not available at this time.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Company;
