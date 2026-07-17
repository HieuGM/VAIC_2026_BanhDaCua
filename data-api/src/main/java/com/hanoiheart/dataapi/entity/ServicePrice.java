package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.math.BigInteger;
import java.time.LocalDate;

/**
 * Price row for a {@link HospitalService} by audience (BHYT / no_bhyt / foreigner).
 * Stored as BigInteger (VND has no fractional currency).
 */
@Entity
@Table(name = "service_prices", schema = "hospital")
public class ServicePrice extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "service_id")
    private HospitalService service;

    @Column(name = "price_vnd", nullable = false)
    private BigInteger priceVnd;

    /** BHYT | no_bhyt | foreigner. */
    @Column(name = "audience", nullable = false, length = 16)
    private String audience;

    /** "CƠ SỞ 1" | "CƠ SỞ 2" | null = both. */
    @Column(name = "campus", length = 16)
    private String campus;

    @Column(name = "effective_date")
    private LocalDate effectiveDate;

    @Column(name = "source_url")
    private String sourceUrl;

    @Column(name = "note")
    private String note;

    public HospitalService getService() { return service; }
    public void setService(HospitalService s) { this.service = s; }
    public BigInteger getPriceVnd() { return priceVnd; }
    public void setPriceVnd(BigInteger p) { this.priceVnd = p; }
    public String getAudience() { return audience; }
    public void setAudience(String a) { this.audience = a; }
    public String getCampus() { return campus; }
    public void setCampus(String c) { this.campus = c; }
    public LocalDate getEffectiveDate() { return effectiveDate; }
    public void setEffectiveDate(LocalDate d) { this.effectiveDate = d; }
    public String getSourceUrl() { return sourceUrl; }
    public void setSourceUrl(String s) { this.sourceUrl = s; }
    public String getNote() { return note; }
    public void setNote(String n) { this.note = n; }
}
