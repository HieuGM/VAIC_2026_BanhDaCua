package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.time.LocalDate;
import java.time.LocalTime;

/**
 * Lịch khám của bác sĩ tại một phòng, một ngày cụ thể.
 */
@Entity
@Table(name = "doctor_schedules", schema = "hospital")
public class DoctorSchedule extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "doctor_id")
    private Doctor doctor;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    /** 1=Mon ... 7=Sun (ISO). */
    @Column(name = "day_of_week")
    private Integer dayOfWeek;

    @Column(name = "effective_date")
    private LocalDate effectiveDate;

    @Column(name = "start_time")
    private LocalTime startTime;

    @Column(name = "end_time")
    private LocalTime endTime;

    /** morning | afternoon | fullday. */
    @Column(name = "shift", length = 16)
    private String shift;

    @Column(name = "room", length = 64)
    private String room;

    @Column(name = "note")
    private String note;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = Boolean.TRUE;

    public Doctor getDoctor() { return doctor; }
    public void setDoctor(Doctor d) { this.doctor = d; }
    public Department getDepartment() { return department; }
    public void setDepartment(Department d) { this.department = d; }
    public Integer getDayOfWeek() { return dayOfWeek; }
    public void setDayOfWeek(Integer d) { this.dayOfWeek = d; }
    public LocalDate getEffectiveDate() { return effectiveDate; }
    public void setEffectiveDate(LocalDate d) { this.effectiveDate = d; }
    public LocalTime getStartTime() { return startTime; }
    public void setStartTime(LocalTime t) { this.startTime = t; }
    public LocalTime getEndTime() { return endTime; }
    public void setEndTime(LocalTime t) { this.endTime = t; }
    public String getShift() { return shift; }
    public void setShift(String s) { this.shift = s; }
    public String getRoom() { return room; }
    public void setRoom(String r) { this.room = r; }
    public String getNote() { return note; }
    public void setNote(String n) { this.note = n; }
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean a) { this.isActive = a; }
}
