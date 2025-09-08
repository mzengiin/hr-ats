/**
 * Turkish phone number mask utility
 */

export const formatTurkishPhone = (value) => {
  // Remove all non-digit characters
  const phoneNumber = value.replace(/\D/g, '');
  
  // If empty, return empty
  if (!phoneNumber) return '';
  
  // If starts with 0, format as: 0XXX XXX XX XX
  if (phoneNumber.startsWith('0')) {
    if (phoneNumber.length <= 4) {
      return phoneNumber;
    } else if (phoneNumber.length <= 7) {
      return `${phoneNumber.slice(0, 4)} ${phoneNumber.slice(4)}`;
    } else if (phoneNumber.length <= 9) {
      return `${phoneNumber.slice(0, 4)} ${phoneNumber.slice(4, 7)} ${phoneNumber.slice(7)}`;
    } else {
      return `${phoneNumber.slice(0, 4)} ${phoneNumber.slice(4, 7)} ${phoneNumber.slice(7, 9)} ${phoneNumber.slice(9, 11)}`;
    }
  }
  // If starts with +90, format as: +90 XXX XXX XX XX
  else if (phoneNumber.startsWith('90')) {
    const withoutCountryCode = phoneNumber.slice(2);
    if (withoutCountryCode.length <= 3) {
      return `+90 ${withoutCountryCode}`;
    } else if (withoutCountryCode.length <= 6) {
      return `+90 ${withoutCountryCode.slice(0, 3)} ${withoutCountryCode.slice(3)}`;
    } else if (withoutCountryCode.length <= 8) {
      return `+90 ${withoutCountryCode.slice(0, 3)} ${withoutCountryCode.slice(3, 6)} ${withoutCountryCode.slice(6)}`;
    } else {
      return `+90 ${withoutCountryCode.slice(0, 3)} ${withoutCountryCode.slice(3, 6)} ${withoutCountryCode.slice(6, 8)} ${withoutCountryCode.slice(8, 10)}`;
    }
  }
  // If starts with 5 (mobile), add 0 and format
  else if (phoneNumber.startsWith('5') && phoneNumber.length >= 10) {
    const withZero = '0' + phoneNumber;
    return formatTurkishPhone(withZero);
  }
  // Default formatting
  else {
    if (phoneNumber.length <= 3) {
      return phoneNumber;
    } else if (phoneNumber.length <= 6) {
      return `${phoneNumber.slice(0, 3)} ${phoneNumber.slice(3)}`;
    } else if (phoneNumber.length <= 8) {
      return `${phoneNumber.slice(0, 3)} ${phoneNumber.slice(3, 6)} ${phoneNumber.slice(6)}`;
    } else {
      return `${phoneNumber.slice(0, 3)} ${phoneNumber.slice(3, 6)} ${phoneNumber.slice(6, 8)} ${phoneNumber.slice(8, 10)}`;
    }
  }
};

export const validateTurkishPhone = (phone) => {
  const phoneNumber = phone.replace(/\D/g, '');
  
  // Turkish mobile numbers: 05XX XXX XX XX (11 digits starting with 05)
  // Turkish landline: 0XXX XXX XXXX (10-11 digits starting with 0)
  if (phoneNumber.startsWith('05') && phoneNumber.length === 11) {
    return true;
  }
  if (phoneNumber.startsWith('0') && phoneNumber.length >= 10 && phoneNumber.length <= 11) {
    return true;
  }
  
  return false;
};
